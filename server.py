from flask import Flask, request, session, render_template
from flask_ask import (
    Ask, 
    statement,
    question,
    session as ask_session ,
    request as ask_request,
    convert_errors
)

import json
import requests
import datetime

app = Flask(__name__)
ask = Ask(app, '/alexa_transloc')

# From my experience, these are the stops most useful for undergraduates.
# It might be worth accessing location info to find nearby stops.
important_stops = [
    4146366, # Duke Chapel
    4188200, # Campus Dr at Swift Ave (Westbound) (12007)
    4188202, # Campus Dr at Swift Ave (Eastbound) (12008)
    4195822, # Swift Ave at 300 Swift (13009)
    4117202, # East Campus Quad (12003)
    4195814, # Smith Warehouse Eastbound (12077)
    4158230, # Smith Warehouse Westbound (12071)
    4197174, # Devil's Bistro (13300)
    4188214, # Swift Avenue Eastbound (12059)
    4195826, # Campus Dr at Nasher (Eastbound) (13015)
    4188204, # Nasher  Westbound (12009)
    4192460, # Oregon St at Pace St (13018)
    4098294, # Alexander Ave at Pace St Eastbound (12056)
    4098274, # Anderson St at Mill Village (12051)
    4098278, # Anderson St at Lewis St (12052)
]

AGENCY_ID = 176 # Duke

@app.route('/')
def testing():
    return ""

@ask.launch
def launch():
    hello = render_template('welcome')
    help_text = render_template('help')
    return question(hello).reprompt('list_stops_reprompt')

@ask.intent('ListStopsIntent')
def supported_stops():
    print("list stops invoked")
    supported = render_template('list_stops', stops=important_stops)
    return question(supported).reprompt('list_stops_reprompt')

@ask.intent('SelectStopIntent', mapping={'stop': 'desired_stop'})
def select_stop(stop):
    if 'stop' in convert_errors:
        return question('Can you please repeat which stop you\'d like?')

    response  = request.get_json()
    stop_info = response['request']['intent']['slots']['desired_stop']
    stop_name = stop_info['value']
    stop_id   = stop_info['resolutions']['resolutionsPerAuthority'][0]['values'][0]['value']['id']

    return statement(stop_times_to_english(int(stop_id)))

@ask.intent('AMAZON.HelpIntent')
def help():
    help_text = render_template('help')
    return question(help_text)

@ask.intent('AMAZON.StopIntent')
def stop():
    bye_text = render_template('bye')
    return statement(bye_text)

@ask.intent('AMAZON.CancelIntent')
def cancel():
    bye_text = render_template('bye')
    return statement(bye_text)

@ask.session_ended
def session_ended():
    return "{}", 200

################### Template Filters 

@app.template_filter()
def humanize_times(times):
    """ Converts a list of bus times to useful english string. """
    english_string = ""
    times = times[:3]

    for t in times[:-1]:
        if t < 60:
            english_string += "less than a minute, "
        else:
            english_string += str(t // 60) + " minutes, "

    if english_string != "":
        english_string += "and "

    if times[-1] < 60:
        english_string += " less than a minute."
    else:
        english_string += str(times[-1] // 60) + " minutes. "

    return english_string

@app.template_filter()
def humanize_stops(stops):
    """ Converts a list of stops to useful english string. """
    english_string = ""
    for stop in stops:
        english_string += stop_id_to_name(stop) + ", "

    return english_string


################### API Handing 

request_headers = {
    "X-Mashape-Key": "MASHAPE API KEY HERE", # request a key at ===> https://market.mashape.com/transloc/openapi-1-2
    "Accept": "application/json"
}

def get_stops():
    """ Returns list of stops for the specified agency. """
    endpoint = "https://transloc-api-1-2.p.mashape.com/stops.json"
    payload = { "agencies": AGENCY_ID, "callback": "call" }
    response = requests.get(endpoint, params=payload, headers=request_headers)
    return response.json()

def get_routes():
    """ Returns list of routes for the specified agency. """
    endpoint = "https://transloc-api-1-2.p.mashape.com/routes.json"
    payload = { "agencies": AGENCY_ID, "callback": "call" }
    response = requests.get(endpoint, params=payload, headers=request_headers)
    return response.json()

def get_arrival_estimates(stop_id):
    """ Returns list of arrival estimates for a certain stop. """
    endpoint = "https://transloc-api-1-2.p.mashape.com/arrival-estimates.json?"
    payload = { "agencies": AGENCY_ID, "stops": str(stop_id), "callback": "call" }
    response = requests.get(endpoint, params=payload, headers=request_headers)
    return response.json()

route_name_map = {}
def route_id_to_name(route_id):
    """ Returns english name for a specific route_id. """
    if len(route_name_map) == 0:
        resp = get_routes()
        for route in resp['data'][str(AGENCY_ID)]:
            name = route["long_name"]
            r_id = route["route_id"]
            route_name_map[str(r_id)] = name

    return route_name_map[str(route_id)]

stop_name_map = {}
def stop_id_to_name(stop_id):
    """ Returns english name for a specific stop_id. """
    if len(stop_name_map) == 0:
        resp = get_stops();
        for stop in resp['data']:
            s_id = stop["stop_id"]
            s_name = stop["name"]
            stop_name_map[str(s_id)] = s_name

    stop_name = stop_name_map[str(stop_id)]
    return stop_name.split(' (')[0] # dumb way to get rid of parenthesis at end

def stop_arrivals(stop_id):
    """ Returns a map of route_ids to arrival times at a specific stop. """
    arrivals = get_arrival_estimates(stop_id)

    route_map = {}
    if len(arrivals['data']) < 1:
        return {} 
    for arrival in arrivals['data'][0]['arrivals']:
        if arrival['route_id'] in route_map:
           route_map[arrival['route_id']].append(arrival['arrival_at'])
        else:
            route_map[arrival['route_id']] = [arrival['arrival_at']]

    return route_map

def stop_times(stop_id):
    """ Returns a map of active routes to wait times for that route at a specific stop. """
    arrival_map = stop_arrivals(stop_id)

    stop_times = {}
    for route_id in arrival_map:
        route_name = route_id_to_name(route_id)
        stop_times[route_name] = []
        current_time = datetime.datetime.now()
        for timestamp in arrival_map[route_id]:
            arrival_time = datetime.datetime.strptime(timestamp,"%Y-%m-%dT%H:%M:%S-04:00")
            stop_times[route_name].append((arrival_time - current_time).seconds)

    return stop_times

def stop_times_to_english(stop_id):
    """ Returns an english string detailing wait times for a specific stop. """
    st = stop_times(stop_id)
    if len(st) < 1:
        return render_template('stop_info_empty', stop_name=stop_id_to_name(stop_id))
    output = render_template('stop_info', stop_name=stop_id_to_name(stop_id))
    for route in st:
        output += render_template('route_info', route_name=route, arrival_times=st[route])

    return output

if __name__ == "__main__":
        app.run()
