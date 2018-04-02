import json
import requests
import datetime


agency_ids = {
    'duke': 176
}

# "Swift Ave at 300 Swift (13009)" =stop id=> 4195822

mashape_key = "AlnhnOmDSUmshGo5NruF8cHoYuHZp10ExI0jsnVyUrVkDc3H4Y"
request_headers = {
    "X-Mashape-Key": mashape_key,
    "Accept": "application/json"
}

def get_stops(agency_id):   
    endpoint = "https://transloc-api-1-2.p.mashape.com/stops.json"
    payload = {
        "agencies": agency_ids['duke'],
        "callback": "call"
    }

    response = requests.get(endpoint, params=payload, headers=request_headers)
    return response.json()


def get_routes(agency_id):
    endpoint = "https://transloc-api-1-2.p.mashape.com/routes.json"

    payload = {
        "agencies": agency_ids['duke'],
        "callback": "call"
    }

    response = requests.get(endpoint, params=payload, headers=request_headers)
    return response.json()

def get_arrival_estimates(stop_id):
    endpoint = "https://transloc-api-1-2.p.mashape.com/arrival-estimates.json?"

    payload = {
        "agencies": agency_ids['duke'],
        "stops": str(stop_id),
        "callback": "call"
    }

    response = requests.get(endpoint, params=payload, headers=request_headers)
    return response.json()

route_name_map = {}
def route_id_to_name(route_id):
    if len(route_name_map) == 0:
        resp = get_routes(176);
        for route in resp['data'][str(176)]:
            name = route["long_name"]
            r_id = route["route_id"]
            route_name_map[str(r_id)] = name

    return route_name_map[str(route_id)]

#???###########################################
stop_name_map = {}
def stop_id_to_name(stop_id):
    if len(stop_name_map) == 0:
        resp = get_stops(176);
        for stop in resp['data']:
            #print(json.dumps(stop,indent=4))
            s_id = stop["stop_id"]
            s_name = stop["name"]
            stop_name_map[str(s_id)] = s_name

    return stop_name_map[str(stop_id)]
#############################A#################

# (route_id, route_name) => stop_id
def route_stops(agency_id):
    resp = get_routes(agency_id)

    route_map = {}
    for route in resp['data'][str(agency_id)]:
        name = route["long_name"]
        route_id = route["route_id"]
        active = route["is_active"]
        route_map[(route_id, name, active)] = route["stops"]

    return route_map

# stop_id => (route_id, route_name)
def stop_routes(agency_id):
    route_map = route_stops(agency_id)

    stop_map = {}
    for route_tuple in route_map:
        for stop in route_map[route_tuple]:
            if stop in stop_map and route_tuple not in stop_map[stop]:
                stop_map[stop].append(route_tuple)
            else:
                stop_map[stop] = [route_tuple]

    return stop_map

# stop_id => map of route_ids to arrival times
def stop_arrivals(agency_id, stop_id):
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


# 
def stop_times(stop_id):
    arrival_map = stop_arrivals(176, stop_id)

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


    



print(json.dumps(stop_arrivals(176,4188202),indent=4))

print(json.dumps(stop_times(4188202),indent=4))
print(json.dumps(stop_times(4188202),indent=4))

print(json.dumps(stop_id_to_name(4188202),indent=4))

