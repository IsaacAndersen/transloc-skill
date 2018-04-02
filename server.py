from flask import Flask, render_template
from flask_ask import Ask, statement, question, session

import json
import requests
import datetime

app = Flask(__name__)
ask = Ask(app, '/alexa_transloc')

@ask.launch
def launch():
    welcome_text = render_template('welcome')
    help_text = render_template('help')
    return question(welcome_text).reprompt(help_text)

@ask.intent('AMAZON.HelpIntent')
def help():
    help_text = render_template('help')
    list_cities_reprompt_text = render_template('list_cities_reprompt')
    return question(help_text).reprompt(list_cities_reprompt_text)


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


#################### API HANDLING ###############################################

desired_stops = [
    4188200, # "Campus Dr at Swift Ave (Westbound) (12007)"
    4195822, # "Swift Ave at 300 Swift (13009)"
]

AGENCY_ID = 176 # Duke
ENDPOINT = "https://transloc-api-1-2.p.mashape.com/"

request_headers = {
    "X-Mashape-Key": "AlnhnOmDSUmshGo5NruF8cHoYuHZp10ExI0jsnVyUrVkDc3H4Y",
    "Accept": "application/json"
}

def get_stops():   
    request_url = ENDPOINT + "stops.json"
    payload = {
        "agencies": AGENCY_ID,
        "callback": "call"
    }

    response = requests.get(request_url, params=payload, headers=request_headers)
    return response.json()


def get_routes():
    request_url = ENDPOINT + "routes.json"
    payload = {
        "agencies": AGENCY_ID,
        "callback": "call"
    }

    response = requests.get(request_url, params=payload, headers=request_headers)
    return response.json()

def get_arrival_estimates(stop_id):
    request_url = ENDPOINT + "arrival-estimates.json?"
    payload = {
        "agencies": AGENCY_ID,
        "stops": str(stop_id),
        "callback": "call"
    }

    response = requests.get(request_url, params=payload, headers=request_headers)
    return response.json()

route_name_map = {}
def route_id_to_name(route_id):
    if len(route_name_map) == 0:
        resp = get_routes()
        for route in resp['data'][AGENCY_ID]:
            name = route["long_name"]
            r_id = route["route_id"]
            route_name_map[str(r_id)] = name

    return route_name_map[str(route_id)]

stop_name_map = {}
def stop_id_to_name(stop_id):
    if len(stop_name_map) == 0:
        resp = get_stops();
        for stop in resp['data']:
            #print(json.dumps(stop,indent=4))
            s_id = stop["stop_id"]
            s_name = stop["name"]
            stop_name_map[str(s_id)] = s_name

    return stop_name_map[str(stop_id)]

# stop_id => map of route_ids to arrival times
def stop_arrivals(stop_id):
    arrivals = get_arrival_estimates(stop_id)

    route_map = {}

    for arrival in arrivals['data'][0]['arrivals']:
        arrival_route = arrival['route_id']
        arrival_time  = arrival['arrival_at']

        if arrival_route in route_map:
           route_map[arrival_route].append(arrival_time)
        else:
            route_map[arrival_route] = [arrival_time]

    return route_map

# stop id => map of routes to wait times
def stop_times(stop_id):
    arrival_map = stop_arrivals(stop_id)

    stop_times = {}
    for route_id in arrival_map:
        route_name = route_id_to_name(route_id)
        stop_times[route_name] = []
        current_time = datetime.datetime.now()
        for timestamp in arrival_map[route_id]:
            arrival_time = datetime.datetime.strptime(timestamp,"%Y-%m-%dT%H:%M:%S-04:00")
            arrival_delta = arrival_time - current_time
            stop_times[route_name].append(arrival_delta.seconds)

    return stop_times