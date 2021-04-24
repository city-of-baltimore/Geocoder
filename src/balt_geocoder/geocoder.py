"""Geocodes addresses through geocod.io with lookup caching"""

import json
import os
import pickle
import re
from functools import wraps
from typing import Any, Callable, cast, Dict, List, Optional, Tuple, Union

import requests
from loguru import logger
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential  # type: ignore

from .geocodio_types import GeocodeResult, GeocodioResult, GeocodioLocation, GeocodioCoordinates, \
    GeocodioAddressComponents, GeocodioCensusField, GeocodioCensusYear, GeocodioCensusYearDict

TFunc = Callable[..., Any]


class APIRetryError(Exception):
    """Exception used when there is a fixable issue with authenticating to the API"""


class APIFatalError(Exception):
    """Exception used when there is a fatal issue wth authenticating to the API"""


def error_check(func: TFunc) -> Callable:
    """Decorator that handles error checking around the geocod.io web call"""
    @wraps(func)
    def wrapper(self, *args, **kwargs) -> Callable:
        if self.geocodio_api_index >= len(self.geocodio_api_list):
            raise APIFatalError('No more valid geocodio APIs to use')

        # This can raise json.JSONDecodeError, but the retry decorators handle that retry condition
        resp = func(self, *args, **kwargs).json()

        if resp.get('results') is not None or resp.get('result') is not None:
            # Valid response
            return resp

        if resp.get('error'):
            # Error condition
            error = resp.get('error')
            if error and (error.startswith('Please add a payment method.') or
                          error.startswith('Invalid API key') or
                          error.startswith('This is just a demo account')):
                logger.warning("API key {} expired.", self.geocodio_api_list[self.geocodio_api_index])
                self.geocodio_api_index += 1
                raise APIRetryError('Geocodio api error')

            if resp.get('error'):
                raise RuntimeError('Geocodio reported error: {}'.format(resp.get('error')))

        raise RuntimeError('Unexpected response: {}'.format(resp))

    return wrapper


class Geocoder:
    """
    Handles lookups to geocodio, while also supporting multiple API keys and result caching
    :param geocodio_api_key: API key provided by Geocod.io
    :param pickle_filename: name of the file to store cached results. If it exists, then cached values will be used.
    :param pickle_filename_rev: name of the file to store cached results. If it exists, then cached values will be used.
    """
    def __init__(self, geocodio_api_key: Union[List[str], str],
                 pickle_filename: str = 'geo.pickle',
                 pickle_filename_rev: str = 'geo_rev.pickle'):
        self.geocodio_api_list = [geocodio_api_key] if isinstance(geocodio_api_key, str) else geocodio_api_key

        # looking for instances where the default wasn't changed
        if len(self.geocodio_api_list) == 1 and self.geocodio_api_list[0] == 'xxx':
            raise ValueError('The GAPI key must be set in creds.py')

        self.geocodio_api_index: int = 0

        self.pickle_filename: str = pickle_filename
        self.pickle_filename_rev: str = pickle_filename_rev

        self.cached_geo: Dict[str, GeocodeResult] = {}
        self.cached_geo_rev: Dict[Tuple[float, float], GeocodeResult] = {}

        if os.path.exists(self.pickle_filename):
            with open(self.pickle_filename, 'rb') as pkl:
                self.cached_geo = pickle.load(pkl)

        if os.path.exists(self.pickle_filename_rev):
            with open(self.pickle_filename_rev, 'rb') as pkl:
                self.cached_geo_rev = pickle.load(pkl)

    def __enter__(self):
        return self

    def __exit__(self, *a):
        with open(self.pickle_filename, 'wb') as proc_files:
            pickle.dump(self.cached_geo, proc_files)

        with open(self.pickle_filename_rev, 'wb') as proc_files:
            pickle.dump(self.cached_geo_rev, proc_files)

    @staticmethod
    def _standardize_address(street_address: str) -> str:
        """The original dataset has addresses formatted in various ways. This attempts to standardize them a bit"""
        street_address = street_address.upper()
        street_address = street_address.replace(' BLK ', ' ')
        street_address = street_address.replace(' BLOCK ', ' ')
        street_address = street_address.replace('JONES FALLS', 'I-83')
        street_address = street_address.replace('JONES FALLS EXPWY', 'I-83')
        street_address = street_address.replace('JONES FALLS EXPRESSWAY', 'I-83')
        street_address = street_address.replace(' HW', ' HWY')
        street_address = re.sub(r'^(\d*) N\.? (.*)', r'\1 NORTH \2', street_address)
        street_address = re.sub(r'^(\d*) S\.? (.*)', r'\1 SOUTH \2', street_address)
        street_address = re.sub(r'^(\d*) E\.? (.*)', r'\1 EAST \2', street_address)
        street_address = re.sub(r'^(\d*) W\.? (.*)', r'\1 WEST \2', street_address)

        return street_address

    def geocode(self, street_address: str) -> Optional[GeocodeResult]:
        """
        Pulls the latitude and longitude of an address, either from the internet, or the cached version
        :param street_address: Address to search. Can be anything that would be searched on google maps.
        :return: Optional GeocodeResult type. If there is an error in the lookup, then it returns None
        """
        logger.info('Get address {address}', address=street_address)
        std_address: str = self._standardize_address(street_address)
        if not self.cached_geo.get(std_address):
            response: GeocodioResult = self._geocode(std_address)

            for loc in response.get('results', []):
                ret: Optional[GeocodeResult] = self.get_geocode_result(loc)

                if ret:
                    ret = cast(GeocodeResult, ret)
                    self.update_cached_geo(ret, forward_lookup=std_address)

        return self.cached_geo.get(std_address)

    def reverse_geocode(self, lat: float, long: float) -> Optional[GeocodeResult]:
        """
        Does a reverse geocode lookup based on the lat/long
        :param lat: Latitude of the point to reverse lookup
        :param long: Longitude of the point to reverse lookup
        :return: A dictionary with location data
        """
        logger.info('Get info for lat/long: {lat}/{long}', lat=lat, long=long)

        if lat is None or long is None:
            return None

        # Four decimal points is more than enough precision
        lat_rnd: float = round(lat, 4)
        long_rnd: float = round(long, 4)

        # if we have a cached result, then skip the lookup
        if not self.cached_geo_rev.get((lat_rnd, long_rnd)):
            response: GeocodioResult = self._reverse_geocode(lat_rnd, long_rnd)

            for loc in response.get('results', []):
                ret: Optional[GeocodeResult] = self.get_geocode_result(loc)

                if ret:
                    ret = cast(GeocodeResult, ret)
                    self.update_cached_geo(ret, rev_lookup=(lat, long))

        return self.cached_geo_rev.get((lat_rnd, long_rnd))

    def update_cached_geo(self, geocode_result: GeocodeResult, forward_lookup: str = None,
                          rev_lookup: Tuple[float, float] = None) -> None:
        """
        Updates the locally cached geo lookup dictionary if geocode_result is a more accurate result
        :param geocode_result: geocode result from Geocod.io
        :param forward_lookup: The uncleaned street address
        :param rev_lookup: The latitude and longitude
        :return: None
        """
        assert geocode_result is not None
        assert geocode_result.get('accuracy')
        result_accuracy: float = geocode_result['accuracy']

        # Update formatted address lookup
        addr: str = cast(str, geocode_result.get('formatted_address', ''))
        if not self.cached_geo.get(addr) or self.cached_geo[addr].get('accuracy', 0.0) < result_accuracy:
            self.cached_geo[addr] = geocode_result

        # Update the uncleaned address lookup
        if forward_lookup:
            if not self.cached_geo.get(forward_lookup) or \
                    self.cached_geo[forward_lookup].get('accuracy', 0.0) < result_accuracy:
                self.cached_geo[forward_lookup] = geocode_result

        # Update the actual coordinate lookup
        coords = None
        if geocode_result.get('latitude') and geocode_result.get('longitude'):
            coords = (round(geocode_result['latitude'], 4), round(geocode_result['longitude'], 4))

            if not self.cached_geo_rev.get(coords) or \
                    self.cached_geo_rev[coords].get('accuracy', 0.0) < result_accuracy:
                self.cached_geo_rev[coords] = geocode_result

        # Update the requested coordinates
        if rev_lookup:
            rev_lookup = (round(rev_lookup[0], 4), round(rev_lookup[1], 4))
            if (not self.cached_geo_rev.get(rev_lookup) or
                    self.cached_geo_rev[rev_lookup].get('accuracy', 0.0) < result_accuracy):
                self.cached_geo_rev[rev_lookup] = geocode_result

    @staticmethod
    def get_geocode_result(geocodio_loc: GeocodioLocation) -> GeocodeResult:
        """
        Processes a json response from the geocodio api and standardizes it
        :param geocodio_loc: The json dictionary from geocodio
        :return: None if there is an error. Otherwise, a dictionary with the GeocodeResult values
        """
        ret: GeocodeResult = {'latitude': 0.0,
                              'longitude': 0.0,
                              'formatted_address': geocodio_loc.get('formatted_address', ''),
                              'accuracy': float(geocodio_loc.get('accuracy', 0.0)),
                              'accuracy_type': geocodio_loc.get('accuracy_type', ''),
                              'source': geocodio_loc.get('source', ''),
                              'number': '',
                              'predirectional': '',
                              'street': '',
                              'suffix': '',
                              'formatted_street': '',
                              'city': '',
                              'county': '',
                              'state': '',
                              'zip': '',
                              'country': '',
                              'census_tract': ''}

        if geocodio_loc.get('address_components'):
            # type checking
            addr_dict: GeocodioAddressComponents = cast(GeocodioAddressComponents,
                                                        geocodio_loc.get('address_components'))

            # We only want city results
            if not addr_dict.get('county', '').upper() == 'BALTIMORE CITY':
                logger.warning('Got non-city result: {loc}', loc=geocodio_loc)

            ret['number'] = addr_dict.get('number', '')
            ret['predirectional'] = addr_dict.get('predirectional', '')
            ret['street'] = addr_dict.get('street', '')
            ret['suffix'] = addr_dict.get('suffix', '')
            ret['formatted_street'] = addr_dict.get('formatted_street', '')
            ret['city'] = addr_dict['city']
            ret['county'] = addr_dict['county']
            ret['state'] = addr_dict['state']
            ret['zip'] = addr_dict['zip']
            ret['country'] = addr_dict['country']

        if geocodio_loc.get('location'):
            # type checking
            loc_dict: GeocodioCoordinates = cast(GeocodioCoordinates, geocodio_loc.get('location'))
            ret['latitude'] = loc_dict['lat']
            ret['longitude'] = loc_dict['lng']

        if geocodio_loc.get('fields'):
            # type checking
            fields_dict: GeocodioCensusField = cast(GeocodioCensusField, geocodio_loc.get('fields', {}))
            if fields_dict.get('census'):
                census_dict: GeocodioCensusYear = cast(GeocodioCensusYear,
                                                       fields_dict.get('census'))  # type checking

                census_year: str = str(next(iter(census_dict.keys())))
                if census_dict.get(census_year):
                    census_year_dict: GeocodioCensusYearDict = cast(GeocodioCensusYearDict,
                                                                    census_dict.get(census_year))  # type checking
                    ret['census_tract'] = census_year_dict['tract_code']

        return ret

    @retry(retry=retry_if_exception_type(RuntimeError) | retry_if_exception_type(json.JSONDecodeError),
           stop=stop_after_attempt(5), wait=wait_exponential(multiplier=1, min=5, max=40), reraise=True)
    @retry(retry=retry_if_exception_type(APIRetryError), reraise=True)
    @error_check
    def _reverse_geocode(self, lat: float, long: float) -> GeocodioResult:
        """Helper that calls the Geocod.io reverse geocode api"""
        payload = {'q': '{},{}'.format({lat}, {long}),
                   'fields': 'census',
                   'api_key': self.geocodio_api_list[self.geocodio_api_index]}
        resp: requests.Response = requests.get('https://api.geocod.io/v1.6/reverse', params=payload)
        return cast(GeocodioResult, resp)  # error_check decorator returns it as this type when it calls json()

    @retry(retry=retry_if_exception_type(RuntimeError) | retry_if_exception_type(json.JSONDecodeError),
           stop=stop_after_attempt(5), wait=wait_exponential(multiplier=1, min=5, max=40), reraise=True)
    @retry(retry=retry_if_exception_type(APIRetryError), reraise=True)
    @error_check
    def _geocode(self, street_address: str) -> GeocodioResult:
        """Helper that calls the Geocod.io geocode api"""
        payload = {'q': street_address,
                   'fields': 'census',
                   'api_key': self.geocodio_api_list[self.geocodio_api_index]}

        resp: requests.Response = requests.get('https://api.geocod.io/v1.6/geocode', params=payload)
        return cast(GeocodioResult, resp)  # error_check decorator returns it as this type when it calls json()
