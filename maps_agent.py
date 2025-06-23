import googlemaps
import os

import warnings
warnings.filterwarnings("ignore")

from dotenv import load_dotenv
load_dotenv()
MAPS_API = os.environ['GMAPS_API_KEY']
gmaps = googlemaps.Client(key=MAPS_API)


def nearest_charging_stations(coords: list[float]):
    '''
    Provides a list of nearest EV charging stations
    '''
    searchstr = 'Nearest charging station'
    location = coords
    chargers = gmaps.places(searchstr, location=coords, radius=10000)
    outdict = []
    for charger in chargers['results']:
        curr_poi = {}
        curr_poi['address'] = charger['formatted_address']
        curr_poi['coordinates'] = charger['geometry']['location']
        curr_poi['name'] = charger['name']
        outdict.append(curr_poi)
    return outdict

def nearest_Kia_service_stations(coords: list[float]):
    '''
    Provides a list of nearest Kia service stations
    '''
    searchstr = 'Nearest Kia Service Stations'
    location = coords
    chargers = gmaps.places(searchstr, location=coords, radius=10000)
    outdict = []
    for charger in chargers['results']:
        curr_poi = {}
        curr_poi['address'] = charger['formatted_address']
        curr_poi['coordinates'] = charger['geometry']['location']
        curr_poi['name'] = charger['name']
        outdict.append(curr_poi)
    return outdict

def nearest_Hyundai_service_stations(coords: list[float]):
    '''
    Provides a list of nearest Hyundai service stations
    '''
    searchstr = 'Nearest Hyundai Service Stations'
    chargers = gmaps.places(searchstr, location=coords, radius=10000)
    outdict = []
    for charger in chargers['results']:
        curr_poi = {}
        curr_poi['address'] = charger['formatted_address']
        curr_poi['coordinates'] = charger['geometry']['location']
        curr_poi['name'] = charger['name']
        outdict.append(curr_poi)
    return outdict


def get_charging_stations(address: str):
    '''
    Takes the user's address as input
    Returns a list of nearest charging stations
    Each element in the list is a dictionary containing the address, coordinates (in latitude and longitude) and name of the location
    '''
    geocode_loc = gmaps.geocode(address)
    if (len(geocode_loc) > 0):
        location = [geocode_loc[0]['geometry']['location']['lat'], geocode_loc[0]['geometry']['location']['lng']]
        #location = [1.2931400376598359,103.8065707219687]
        return nearest_charging_stations(location)
    else:
        return []

def get_Kia_service_stations(address: str):
    '''
    Takes the user's address as input
    Returns a list of nearest Kia service stations
    Each element in the list is a dictionary containing the address, coordinates (in latitude and longitude) and name of the location
    '''
    geocode_loc = gmaps.geocode(address)
    if (len(geocode_loc) > 0):
        location = [geocode_loc[0]['geometry']['location']['lat'], geocode_loc[0]['geometry']['location']['lng']]
        #location = [1.2931400376598359,103.8065707219687]
        return nearest_Kia_service_stations(location)
    else:
        return []

def get_Hyundai_service_stations(address: str):
    '''
    Takes the user's address as input
    Returns a list of nearest Hyundai service stations
    Each element in the list is a dictionary containing the address, coordinates (in latitude and longitude) and name of the location
    '''
    geocode_loc = gmaps.geocode(address)
    if (len(geocode_loc) > 0):
        location = [geocode_loc[0]['geometry']['location']['lat'], geocode_loc[0]['geometry']['location']['lng']]
        #location = [1.2931400376598359,103.8065707219687]
        return nearest_Hyundai_service_stations(location)
    else:
        return []

