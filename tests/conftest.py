"""Pytest directory-specific hook implementations"""
import os
import pickle

import pytest

from . import geocoder_constants

from balt_geocoder import Geocoder  # pylint:disable=wrong-import-position,wrong-import-order  # noqa: E402


def pytest_addoption(parser):
    """Adds command line options"""
    parser.addoption("--apikey", action="store")


@pytest.fixture(name='api_key')
def api_key_fixture(request):
    """Command line argument for the API key"""
    api_key = request.config.getoption("apikey")
    assert api_key, "Expected --apikey to be provided"
    return api_key


@pytest.fixture
def geocoder_fixture(api_key, tmpdir):
    """Fixture for the Geocoder class"""
    return Geocoder(api_key, os.path.join(tmpdir, 'geo.pickle'), os.path.join(tmpdir, 'revgeo.pickle'))


@pytest.fixture
def geocoder_fixture_bad_api(tmpdir):
    """Fixture for the Geocoder class with a bad API key"""
    return Geocoder('BADAPI', os.path.join(tmpdir, 'geo.pickle'), os.path.join(tmpdir, 'revgeo.pickle'))


@pytest.fixture
def geocoder_fixture_demo_api(tmpdir):
    """Fixture for the Geocoder class with a quickly exhaustible API key"""
    return Geocoder('DEMO', os.path.join(tmpdir, 'geo.pickle'), os.path.join(tmpdir, 'revgeo.pickle'))


@pytest.fixture
def geocoder_fixture_bad_and_good_api(api_key, tmpdir):
    """Fixture for the Geocoder class that has a bad API key followed by a good key"""
    return Geocoder(['BADAPI', api_key], os.path.join(tmpdir, 'geo.pickle'), os.path.join(tmpdir, 'revgeo.pickle'))


@pytest.fixture
def geocache_files(tmpdir):
    """Sets up the pickle files used by Geocode for address caching"""
    geocode_dict = {'123 TEST RD': geocoder_constants.test_geocode_result}
    forward_geo_file = tmpdir.join('cached.pickle')
    with open(forward_geo_file, 'wb') as fgf:
        pickle.dump(geocode_dict, fgf)

    geocode_rev_dict = {(55.55, 66.66): geocoder_constants.test_geocode_result}
    rev_geo_file = tmpdir.join('cached_rec.pickle')
    with open(rev_geo_file, 'wb') as rgf:
        pickle.dump(geocode_rev_dict, rgf)

    return forward_geo_file, rev_geo_file
