"""Test suite for src.geocoder"""
import sys
from pathlib import Path

import pytest

from . import geocoder_constants

sys.path.insert(0, str(Path.cwd().parent))

from src.geocoder import APIFatalError, \
    Geocoder  # pylint:disable=wrong-import-position,wrong-import-order  # noqa: E402


def _validate_geocode_result(expected, actual):
    assert (actual['latitude'] - .001) <= expected['latitude'] <= (actual['latitude'] + .001)
    assert (actual['longitude'] - .001) <= expected['longitude'] <= (actual['longitude'] + .001)
    assert expected['number'] == actual['number']
    assert expected['predirectional'] == actual['predirectional']
    assert expected['street'] == actual['street']
    assert expected['suffix'] == actual['suffix']
    assert expected['formatted_street'] == actual['formatted_street']
    assert expected['city'] == actual['city']
    assert expected['county'] == actual['county']
    assert expected['state'] == actual['state']
    assert expected['zip'] == actual['zip']
    assert expected['country'] == actual['country']
    assert expected['formatted_address'] == actual['formatted_address']
    assert expected['census_tract'] == actual['census_tract']
    assert expected['accuracy'] == actual['accuracy']
    assert expected['accuracy_type'] == actual['accuracy_type']


def test_api_invalid(geocoder_fixture_bad_api):
    """Testing the case of an invalid API key, which should error"""
    with pytest.raises(APIFatalError):
        geocoder_fixture_bad_api.geocode('123 Main St')


def test_api_exhaust(geocoder_fixture_demo_api):
    """Testing the case of a good API key that hits its limit"""
    with pytest.raises(APIFatalError):
        i = 0
        while i < 10:
            geocoder_fixture_demo_api.geocode('123 Main St')
            i += 1


def test_api_bad_and_good_key(geocoder_fixture_bad_and_good_api):
    """Testing the logic that iterates through API keys to find a good one"""
    ret = geocoder_fixture_bad_and_good_api.geocode('1309 N Charles St Baltimore')
    _validate_geocode_result(geocoder_constants.geocode_result_data, ret)


def test_standardize_address(geocoder_fixture):
    """Tests the standardize_address method"""
    assert geocoder_fixture._standardize_address(  # pylint:disable=protected-access
        '1000 block n charles st') == '1000 NORTH CHARLES ST'
    assert geocoder_fixture._standardize_address(  # pylint:disable=protected-access
        '1000 wilkins ave') == '1000 WILKINS AVE'


def test_geocode(geocoder_fixture):
    """Tests the public geocode method"""
    ret = geocoder_fixture.geocode('1309 N Charles St Baltimore MD')
    _validate_geocode_result(geocoder_constants.geocode_result_data, ret)


def test_reverse_geocode(geocoder_fixture):
    """Tests the public reverse geocode method"""
    ret = geocoder_fixture.reverse_geocode(39.3051, -76.6158)
    _validate_geocode_result(geocoder_constants.geocode_rev_result_data, ret)


def test_get_geocode_result(geocoder_fixture):
    """Tests the get_geocode_result method"""
    ret = geocoder_fixture.get_geocode_result(geocoder_constants.test_get_geocode_result_const['result'][0])
    _validate_geocode_result(ret, geocoder_constants.geocode_result_data)


def test_reverse_geocode_internal(geocoder_fixture):
    """Tests the internal version of the reverse geocode method"""
    ret = geocoder_fixture._reverse_geocode(39.3051, -76.6158)  # pylint:disable=protected-access

    result_list = ret['results']
    assert isinstance(result_list, list)
    assert len(result_list) >= 1

    assert isinstance(result_list[0]['address_components'], dict)
    assert result_list[0]['address_components']['number'] == '1309'
    assert result_list[0]['address_components']['predirectional'] == 'N'
    assert result_list[0]['address_components']['street'] == 'Charles'
    assert result_list[0]['address_components']['suffix'] == 'St'
    assert result_list[0]['address_components']['formatted_street'] == 'N Charles St'
    assert result_list[0]['address_components']['city'] == 'Baltimore'
    assert result_list[0]['address_components']['county'] == 'Baltimore city'
    assert result_list[0]['address_components']['state'] == 'MD'
    assert result_list[0]['address_components']['zip'] == '21201'
    assert result_list[0]['address_components']['country'] == 'US'

    assert result_list[0]['formatted_address'] == '1309 N Charles St, Baltimore, MD 21201'

    assert round(result_list[0]['location']['lat'], 3) == 39.305
    assert round(result_list[0]['location']['lng'], 3) == -76.616

    assert result_list[0]['accuracy'] == 1
    assert result_list[0]['accuracy_type'] == 'rooftop'
    assert result_list[0]['source']
    assert isinstance(result_list[0]['fields'], dict)


def test_geocode_internal(geocoder_fixture):
    """Tests the internal version of the geocode method"""
    ret = geocoder_fixture._geocode('1309 N Charles St Baltimore MD')  # pylint:disable=protected-access

    assert isinstance(ret['input'], dict)
    assert isinstance(ret['results'], list)

    res = ret['results'][0]

    assert res['address_components']
    assert res['formatted_address'] == '1309 N Charles St, Baltimore, MD 21202'

    assert round(res['location']['lat'], 3) == 39.305
    assert round(res['location']['lng'], 3) == -76.616

    assert res['accuracy'] == 1
    assert res['accuracy_type'] == 'rooftop'
    assert res['source']
    assert isinstance(res['fields'], dict)


def test_cached_geocode(geocache_files, api_key):
    """Tests a geocode lookup on a cached address"""
    with Geocoder(api_key, geocache_files[0], geocache_files[1]) as gcf:
        res = gcf.geocode('123 TEST RD')
        _validate_geocode_result(geocoder_constants.test_geocode_result, res)


def test_cached_reverse_geocode(geocache_files, api_key):
    """Tests a reverse geocode lookup on a cached address"""
    with Geocoder(api_key, geocache_files[0], geocache_files[1]) as gcf:
        res = gcf.reverse_geocode(55.55, 66.66)
        _validate_geocode_result(geocoder_constants.test_geocode_result, res)


def test_update_cached_geo(geocache_files, api_key):
    """Tests the ability for the cach to be updated when applicable"""
    with Geocoder(api_key, geocache_files[0], geocache_files[1]) as gcf:
        # verify the starting values
        res = gcf.geocode('123 TEST RD')
        _validate_geocode_result(geocoder_constants.test_geocode_result, res)
        res = gcf.reverse_geocode(55.55, 66.66)
        _validate_geocode_result(geocoder_constants.test_geocode_result, res)

        gcf.update_cached_geo(geocoder_constants.test_update_cached_geo_data,
                              forward_lookup='123 TEST RD',
                              rev_lookup=(55.55, 66.66))
        # make sure they updated
        res = gcf.geocode('123 TEST RD')
        _validate_geocode_result(geocoder_constants.test_update_cached_geo_data, res)
        res = gcf.reverse_geocode(55.55, 66.66)
        _validate_geocode_result(geocoder_constants.test_update_cached_geo_data, res)

        # Updates from the formatted address and the lat/long in the data
        res = gcf.geocode('TESTFORMATTEDADDRESS')
        _validate_geocode_result(geocoder_constants.test_update_cached_geo_data, res)
        res = gcf.reverse_geocode(66.66, 77.77)
        _validate_geocode_result(geocoder_constants.test_update_cached_geo_data, res)
