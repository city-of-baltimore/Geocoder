"""Geocodes addresses through geocod.io with lookup caching"""

import json
import logging
import os
import pickle
import re
from typing import List, Optional
from retrying import retry  # type: ignore

import requests

from .geocodio_types import CachedGeoType, GeocodeResult, GeocodioResult

logging.getLogger(__name__)


# Note: We disable unsubscriptable-object because of bug bug: https://github.com/PyCQA/pylint/issues/3882 in pylint.
# When that is fixed, we can remove the pylint unscriptable object disables


def retry_if_runtime_error(exception: Exception) -> bool:
    """Return True if we should retry, False otherwise"""
    return isinstance(exception, RuntimeError)


def error_check(func) -> Optional[GeocodeResult]:
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

        if req.json().get("error"):
            logging.error("Geocodio reported error: %s", req.json().get("error"))
            return None
        return self.get_geocode_result(req)

    return inner


class Geocoder:
    """Handles lookups to geocodio, while also supporting multiple API keys and result caching"""

    def __init__(self, geocodio_api_key: List[str], pickle_filename: str = 'geo.pickle'):
        self.geocodio_api_list = geocodio_api_key
        if len(self.geocodio_api_list) == 1 and self.geocodio_api_list[0] == 'xxx':
            raise ValueError("The GAPI key must be set in creds.py")

        self.geocodio_api_index: int = 0
        self.geocode_url: str = "https://api.geocod.io/v1.6/geocode?q={addr}&fields=census&api_key={api}"
        self.rev_geocode_url: str = "https://api.geocod.io/v1.6/reverse?q={lat},{long}&fields=census&api_key={api}"
        self.pickle_filename: str = pickle_filename
        self.cached_geo: CachedGeoType = {}

    def __enter__(self):
        if os.path.exists(self.pickle_filename):
            with open(self.pickle_filename, 'rb') as pkl:
                self.cached_geo = pickle.load(pkl)

    def __exit__(self, *a):
        with open(self.pickle_filename, 'wb') as proc_files:
            pickle.dump(self.cached_geo, proc_files)

    @staticmethod
    def _standardize_address(street_address: str) -> str:
        street_address = street_address.upper()
        street_address = re.sub(r'^(\d*) N\.? (.*)', r'\1 NORTH \2', street_address)
        street_address = re.sub(r'^(\d*) S\.? (.*)', r'\1 SOUTH \2', street_address)
        street_address = re.sub(r'^(\d*) E\.? (.*)', r'\1 EAST \2', street_address)
        street_address = re.sub(r'^(\d*) W\.? (.*)', r'\1 WEST \2', street_address)
        street_address = street_address.replace(' BLK ', ' ')

        return street_address

    def geocode(self, street_address: str) -> Optional[GeocodeResult]:  # pylint:disable=unsubscriptable-object
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

            # Save as the original formatted address, the reformatted version, and the reverse lookup
            self.cached_geo[street_address] = ret
            self.cached_geo[ret["Street Address"]] = ret
            self.cached_geo[(ret['latitude'], ret['longitude'])] = ret

        return self.cached_geo.get(street_address)

    def reverse_geocode(self, lat: float, long: float) -> Optional[GeocodeResult]:
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
    def get_geocode_result(response) -> Optional[GeocodeResult]:  # pylint:disable=unsubscriptable-object
        """
        Processes a response from the geocodio api and standardizes it
        :param response: The raw response from geocodio
        :return: None if there is an error. Otherwise, a dictionary with the following values: Latitude, Longitude,
        Street Address, Street Num, Street Name, City, GeoState, Zip, Census Tract
        """
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

            return {"latitude": geocode_result["location"]["lat"],
                    "longitude": geocode_result["location"]["lng"],
                    "street_address": geocode_result["formatted_address"],
                    "street_num": geocode_result["address_components"].get("number"),
                    "street_name": geocode_result["address_components"].get("formatted_street"),
                    "city": geocode_result["address_components"]["city"],
                    "state": geocode_result["address_components"]["state"],
                    "zip": geocode_result["address_components"]["zip"],
                    "census_tract": geocode_result["fields"]["census"][census_year]["tract_code"]}
        except IndexError:
            return None

    @retry(wait_exponential_multiplier=1000,
           wait_exponential_max=10,
           retry_on_exception=retry_if_runtime_error)
    @error_check
    def _reverse_geocode(self, lat: float, long: float) -> List[GeocodeResult]:
        resp: GeocodioResult = requests.get(self.rev_geocode_url.format(lat=lat, long=long,
                                                                        api=self.geocodio_api_list[
                                                                            self.geocodio_api_index])).json()
        return resp.get('results')

    @retry(wait_exponential_multiplier=1000,
           wait_exponential_max=10,
           retry_on_exception=retry_if_runtime_error)
    @error_check
    def _geocode(self, street_address: str) -> List[GeocodeResult]:
        resp: GeocodioResult = requests.get(self.geocode_url.format(addr=street_address,
                                                                    api=self.geocodio_api_list[
                                                                        self.geocodio_api_index])).json()
        return resp.get('results')
