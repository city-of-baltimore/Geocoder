"""Pytest directory-specific hook implementations"""
import pickle
import sys
from pathlib import Path
import tempfile

import pytest

from . import geocoder_constants

sys.path.insert(0, str(Path.cwd().parent))

from src import Geocoder  # pylint:disable=wrong-import-position,wrong-import-order  # noqa: E402


def pytest_addoption(parser):
    """Adds command line options"""
    parser.addoption("--apikey", action="store")


@pytest.fixture(name='api_key')
def api_key_fixture(request):
    """Command line argument for the API key"""
    return request.config.getoption("apikey")


@pytest.fixture
def geocoder_fixture(api_key):
    """Fixture for the Geocoder class"""
    with tempfile.TemporaryFile() as forward_geo:
        with tempfile.TemporaryFile() as rev_geo:
            ret = Geocoder(api_key, forward_geo.name, rev_geo.name)
    return ret


@pytest.fixture
def geocoder_fixture_bad_api():
    """Fixture for the Geocoder class with a bad API key"""
    with tempfile.TemporaryFile() as forward_geo:
        with tempfile.TemporaryFile() as rev_geo:
            ret = Geocoder('BADAPI', forward_geo.name, rev_geo.name)
    return ret


@pytest.fixture
def geocoder_fixture_demo_api():
    """Fixture for the Geocoder class with a quickly exhaustible API key"""
    with tempfile.TemporaryFile() as forward_geo:
        with tempfile.TemporaryFile() as rev_geo:
            ret = Geocoder('DEMO', forward_geo.name, rev_geo.name)
    return ret


@pytest.fixture
def geocoder_fixture_bad_and_good_api(api_key):
    """Fixture for the Geocoder class that has a bad API key followed by a good key"""
    with tempfile.TemporaryFile() as forward_geo:
        with tempfile.TemporaryFile() as rev_geo:
            ret = Geocoder(['BADAPI', api_key], forward_geo.name, rev_geo.name)
    return ret


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
