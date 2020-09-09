"""Geocodes addresses through geocod.io with lookup caching"""

import json
import logging
import os
import pickle
import re
import requests
from retrying import retry


logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')


def retry_if_runtime_error(exception):
    """Return True if we should retry, False otherwise"""
    return isinstance(exception, RuntimeError)


def error_check(func):
    """
    Decorator that handles error checking around the geocod.io web call
    :param func:
    :return:
    """
    def inner(self, *args, **kwargs):
        if self.geocodio_api_index >= len(self.geocodio_api_list):
            return None
        req = func(self, *args, **kwargs)
        if req.json().get("error") and req.json().get("error").startswith('Please add a payment method.'):
            self.geocodio_api_index += 1
            raise RuntimeError('Geocodio api error')
        elif req.json().get("error"):
            logging.error(req.json().get("error"))
            return None
        return self._get_geocode_result(req)
    return inner


class Geocoder:
    """Handles lookups to geocodio, while also supporting multiple API keys and result caching"""
    def __init__(self, geocodio_api_key, pickle_filename='geo.pickle'):
        if isinstance(geocodio_api_key, str):
            self.geocodio_api_list = [geocodio_api_key]
        elif isinstance(geocodio_api_key, list):
            self.geocodio_api_list = geocodio_api_key
        elif len(self.geocodio_api_list) == 1 and self.geocodio_api_list[0] == 'xxx':
            raise ValueError("The GAPI key must be set in creds.py")
        else:
            raise TypeError("geocodio_api_key is of wrong type")

        self.geocodio_api_index = 0
        self.geocode_url = "https://api.geocod.io/v1.6/geocode?q={addr}&fields=census&api_key={api}"
        self.rev_geocode_url = "https://api.geocod.io/v1.6/reverse?q={lat},{long}&fields=census&api_key={api}"
        self.pickle_filename = pickle_filename
        self.cached_geo = {}

    def __enter__(self):
        if os.path.exists(self.pickle_filename):
            with open(self.pickle_filename, 'rb') as pkl:
                self.cached_geo = pickle.load(pkl)

    def __exit__(self, *a):
        with open(self.pickle_filename, 'wb') as proc_files:
            pickle.dump(self.cached_geo, proc_files)

    @staticmethod
    def _standardize_address(street_address):
        street_address = street_address.upper()
        street_address = re.sub(r'^(\d*) N\.? (.*)', r'\1 NORTH \2', street_address)
        street_address = re.sub(r'^(\d*) S\.? (.*)', r'\1 SOUTH \2', street_address)
        street_address = re.sub(r'^(\d*) E\.? (.*)', r'\1 EAST \2', street_address)
        street_address = re.sub(r'^(\d*) W\.? (.*)', r'\1 WEST \2', street_address)

        return street_address

    def geocode(self, street_address) -> dict:
        """
        Pulls the latitude and longitude of an address, either from the internet, or the cached version
        :param street_address: Address to search. Can be anything that would be searched on google maps.
        :return: Dictionary with the keys Block_Start, Street_Name, Census_Tract, Street_Address, Block_Start,
        Block_End, Street_Dir, Street_Name, Suffix_Type, Suffix_Direction, Suffix_Qualifier, City, GeoState, Zip,
        Latitude, Longitude. If there is an error in the lookup, then it returns None
        """
        logging.info("Get address %s", street_address)
        street_address = self._standardize_address(street_address)
        if not self.cached_geo.get(street_address):
            ret = self._geocode(street_address)
            if ret is None:
                return None

            # Save as both the original formatted address, and the reformatted version
            self.cached_geo[street_address] = ret
            self.cached_geo[ret["Street Address"]] = ret

        return self.cached_geo.get(street_address)

    def reverse_geocode(self, lat, long):
        """
        Does a reverse geocode lookup based on the lat/long
        :param lat: Latitude of the point to reverse lookup
        :param long: Longitude of the point to reverse lookup
        :return: A dictionary with location data EX:
        {'Latitude': 39.325564, 'Longitude': -76.592078, 'Street Address': '1638 E 30th St, Baltimore, MD 21218',
        'Street Num': '1638', 'Street Name': 'E 30th St', 'City': 'Baltimore', 'GeoState': 'MD', 'Zip': '21218',
        'Census Tract': '090600'}
        """
        logging.info("Get info for lat/long: %s/%s", lat, long)

        if not (isinstance(lat, (int, float)) and isinstance(long, (int, float))):
            logging.error("Invalid lat/long")
            return None

        # Four decimal points is more than enough precision
        lat = round(lat, 4)
        long = round(long, 4)

        if not self.cached_geo.get((lat, long)):
            ret = self._reverse_geocode(lat, long)
            if ret is None:
                return None
            self.cached_geo[(lat, long)] = ret
        return self.cached_geo.get((lat, long))

    @staticmethod
    def _get_geocode_result(response):
        try:
            geocode_result = response.json()["results"]
        except json.JSONDecodeError:
            logging.error("JSON ERROR: %s", response)
            return None

        if len(geocode_result) > 1:
            logging.debug("Multiple results.\n\nResults: %s", geocode_result)
            geocode_result = None

            for res in response.json()["results"]:
                if res["address_components"]["county"].lower() == "baltimore city":
                    geocode_result = res
                    break

            if geocode_result is None:
                return None

        elif len(geocode_result) == 0:
            logging.error("No results.\n\nResults: %s", geocode_result)
            return None
        else:
            geocode_result = geocode_result[0]

        try:
            census_year = next(iter(geocode_result["fields"]["census"].keys()))

            return {"Latitude": geocode_result["location"]["lat"],
                    "Longitude": geocode_result["location"]["lng"],
                    "Street Address": geocode_result["formatted_address"],
                    "Street Num": geocode_result["address_components"].get("number"),
                    "Street Name": geocode_result["address_components"].get("formatted_street"),
                    "City": geocode_result["address_components"]["city"],
                    "GeoState": geocode_result["address_components"]["state"],
                    "Zip": geocode_result["address_components"]["zip"],
                    "Census Tract": geocode_result["fields"]["census"][census_year]["tract_code"]}
        except IndexError:
            return None

    @retry(wait_exponential_multiplier=1000,
           wait_exponential_max=10,
           retry_on_exception=retry_if_runtime_error)
    @error_check
    def _reverse_geocode(self, lat, long) -> object:
        return requests.get(self.rev_geocode_url.format(lat=lat, long=long,
                                                        api=self.geocodio_api_list[self.geocodio_api_index]))

    @retry(wait_exponential_multiplier=1000,
           wait_exponential_max=10,
           retry_on_exception=retry_if_runtime_error)
    @error_check
    def _geocode(self, street_address) -> object:
        return requests.get(self.geocode_url.format(addr=street_address,
                                                    api=self.geocodio_api_list[self.geocodio_api_index]))
