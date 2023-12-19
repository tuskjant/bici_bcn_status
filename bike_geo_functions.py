import requests
import json
import polyline


LAT_1000M = 0.009
LONG_1000M = 0.01196


def get_bicing_data():
    """Retrieves bicing service station status from citybik api
    :returns json data with satatus"""

    citybik_bicing = "http://api.citybik.es/v2/networks/bicing"
    param = {
        "fields": "stations"
    }
    response = requests.get(url=citybik_bicing, params=param)
    response.raise_for_status()
    data = response.json()
    return data


def get_address_coordinates(address_string: str):
    """Retrieves location coordinates from cartociudad api
    :param adrress in string format
    :returns tuple with latitude, longitude in G.GGGGGG format, if
     not found returns False"""

    url_cartociudad = "https://www.cartociudad.es/geocoder/api/geocoder/findJsonp"
    parameters = {
        "q": address_string
    }

    response = requests.get(url=url_cartociudad, params=parameters)
    response.raise_for_status()

    result = response.text.replace('callback(', '')[:-1]
    result = json.loads(result)
    if len(result)>0 and "lat" in result.keys() and "lng" in result.keys():
        lat = result["lat"]
        long = result["lng"]
        return (lat, long)
    else:
        return False


def convert_bicing_data(raw_data):
    """Convert row data received from api to a new list of stations dict
    :param raw data in json format
    :returns list of stations dict"""
    new_stations = []
    stations = raw_data["network"]["stations"]
    for station in stations:
        new_station = {}
        for key, value in station.items():
            if key in ["id", "timestamp", "name", "latitude", "longitude", "empty_slots"]:
                new_station[key] = station[key]
            if key == "extra":
                for subkey in station["extra"].keys():
                    if subkey in ["address", "renting", "returning", "normal_bikes", "ebikes"]:
                        new_station[subkey] = station[key][subkey]
        new_stations.append(new_station)
    return new_stations


def get_nearest_st(coords, st_data):
    """Select the nearest five stations of a given location. All stations must be within approximately 2000m
    square from location.
    :param  coords: latitude, longitude tuple
            st_data: list of stations dict
    :returns list of stations dict filtered and ordered by distance"""
    # Square filter 1000m
    filtered_data = []
    for data in st_data:
        if coords[0] - LAT_1000M < data["latitude"] < coords[0] + LAT_1000M:
            if coords[1] - LONG_1000M < data["longitude"] < coords[1] + LONG_1000M:
                filtered_data.append(data)
    # Fly pseudodistance in degrees
    for item in filtered_data:
        item_lat = item.get("latitude")
        item_long = item.get("longitude")
        dist = ((item_lat - coords[0]) ** 2 + (item_long - coords[1]) ** 2) ** 0.5
        item["distance_deg"] = dist
    # Return  nearest 5
    nearest_5 = sorted(filtered_data, key=lambda d: d['distance_deg'])
    return nearest_5[:5]


def calculate_route(coords_ini, coords_end):
    """Retrieves route data from cartociudad api given an initial and ending point.
    Route calculated using manhattan distance by walk. Description in spanish
    :param  coords_ini: latitude, longitude tuple of initial point
            coords_end: latitude, longitude tuple of ending point
    :returns route data in json format"""
    url_cartociudad_route = "http://www.cartociudad.es/services/api/route"
    param_route = {"orig": f"{coords_ini[0]},{coords_ini[1]}",
                   "dest": f"{coords_end[0]},{coords_end[1]}",
                   "locale": "es",
                   "vehicle": "WALK"}
    response = requests.get(url=url_cartociudad_route, params=param_route)
    response.raise_for_status()
    data = response.json()
    return data


def convert_route(route_data):
    """Convert raw route data into a list of routes to be processed
    :param route_data dict with raw route_data
    :returns list of processed data"""
    new_route = {}
    new_route["geom"] = polyline.decode(route_data["geom"], 5)
    new_route["dist"] = round(float(route_data["distance"]))
    new_route["time"] = round(float(route_data["time"])/6000)
    descr = []
    instruction_list = route_data["instructionsData"]["instruction"]
    for step in instruction_list:
        desc = step['description']
        dst = step['distance']
        descr.append(f"{desc} ({dst})")
        new_route["description"] = descr
    return new_route


def check_st_options(list_st:list, option:str):
    """Selects stations that have empty slots, normal bikes or bikes depending on option selected.
     Sorted by distance prioritizing those with more than 1 slot or bike.
    :param  list_st: list of stations and routes
            option: string with option to check ["empty_slots", "normal_bikes", "ebikes"]
    :return list of sorted stations and routes"""
    if option not in ["empty_slots", "normal_bikes", "ebikes"]:
        return False
    new_list_1 = []
    new_list_2 = []
    # Prioritize stations with more than one slot or bike
    for st in list_st:
        if st[option] > 1:
            new_list_1.append(st)
        elif st[option] > 0:
            new_list_2.append(st)
    new_list_1 = sorted(new_list_1, key=lambda d: d['dist'])
    new_list_2 = sorted(new_list_2, key=lambda d: d['dist'])
    return new_list_1 + new_list_2

def get_stations_data(position:tuple, type:str):
    """Get and prepare data from bicing stations depending on current position and option to consult selected
    :param  position: tuple with user coordinates position
            type: string with option to consult in  ["empty_slots", "normal_bikes", "ebikes"]
    :returns list of 3 nearest stations"""
    # Get bicing service data
    bicing_st = get_bicing_data()
    if bicing_st:
        # Convert bicing data ang get nearest 3 stations
        bicing_st_list = convert_bicing_data(bicing_st)
        nearest_bicing_st = get_nearest_st(position, bicing_st_list)
        # Calculate routes and convert data to dict
        all_routes = []
        for bicing_station in nearest_bicing_st:
            route = calculate_route(position, (bicing_station["latitude"], bicing_station["longitude"]))
            route_mod = convert_route(route)
            route_mod.update(bicing_station)
            all_routes.append(route_mod)
        # Check st that fits user option to search
        user_op = ["empty_slots", "normal_bikes", "ebikes"][type-1]
        ordered_list = check_st_options(all_routes, user_op)
        return ordered_list[:3]

def calculate_bounding_box(data_list):
    """Given a list of data with geom attribute gets the bounding box for all geometries"""
    x = []
    y = []
    for data in data_list:
        geom = data['geom']
        for point in geom:
            x.append(point[0])
            y.append(point[1])
    top_left = (max(x), min(y))
    bottom_right = (min(x), max(y))
    return (top_left, bottom_right)



