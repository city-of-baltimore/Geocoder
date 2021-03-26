"""Defines types used by Geocodio"""
from typing import Dict, List, Optional, TypedDict  # pylint:disable=inherit-non-class ; https://github.com/PyCQA/pylint/issues/3876

# Note: We disable unsubscriptable-object because of bug bug: https://github.com/PyCQA/pylint/issues/3882 in pylint.
# When that is fixed, we can remove the pylint unscriptable object disables


class GeocodioAddressComponents(TypedDict):  # pylint:disable=inherit-non-class,too-few-public-methods
    """Dictionary used in the address_component of Geocodio locations. Used only for typing."""
    number: Optional[str]  # pylint:disable=unsubscriptable-object
    predirectional: Optional[str]  # pylint:disable=unsubscriptable-object
    street: Optional[str]  # pylint:disable=unsubscriptable-object
    suffix: Optional[str]  # pylint:disable=unsubscriptable-object
    formatted_street: Optional[str]  # pylint:disable=unsubscriptable-object
    city: str
    county: str
    state: str
    zip: Optional[str]  # pylint:disable=unsubscriptable-object
    country: str


class GeocodioCoordinates(TypedDict):  # pylint:disable=inherit-non-class,too-few-public-methods
    """Dictionary used as the coordnates in geocodio results. Used only for typing."""
    lat: float
    lng: float


class GeocodioCensusYearDict(TypedDict):  # pylint:disable=inherit-non-class,too-few-public-methods
    """Census year data"""
    census_year: int
    state_fips: str
    county_fips: str
    tract_code: str
    block_code: str
    block_group: str
    full_fips: str
    place: Dict
    metro_micro_statistical_area: Dict
    combined_statistical_area: Dict
    metropolitan_division: Optional[str]  # pylint:disable=unsubscriptable-object
    source: str


# Dict that contains a year and dictionary. This year is dynamic, and I don't know the syntax to do this
GeocodioCensusYear = TypedDict("GeocodioCensusYear", {"2019": GeocodioCensusYearDict})


class GeocodioCensusField(TypedDict):  # pylint:disable=inherit-non-class,too-few-public-methods
    """Geocodio field information for census tracts. Not filled in because we don't use it"""
    census: GeocodioCensusYear


class GeocodioLocation(TypedDict):  # pylint:disable=inherit-non-class,too-few-public-methods
    """Dictionary used as the input and results in geocodio results. Used only for typing."""
    address_components: GeocodioAddressComponents
    formatted_address: str
    location: Optional[GeocodioCoordinates]  # pylint:disable=unsubscriptable-object
    accuracy: float
    accuracy_type: str
    source: str
    fields: Optional[GeocodioCensusField]  # pylint:disable=unsubscriptable-object


class GeocodioResult(TypedDict):  # pylint:disable=inherit-non-class,too-few-public-methods
    """Dictionary used as the result to Geocodio queries. Used only for typing."""
    input: Optional[GeocodioLocation]  # pylint:disable=unsubscriptable-object
    results: List[GeocodioLocation]  # pylint:disable=unsubscriptable-object


class GeocodioErrorResult(TypedDict):  # pylint:disable=inherit-non-class,too-few-public-methods
    """Dictionary used as the result when a Geocodio query fails. Used only for typing."""
    error: str


class GeocodeResult(GeocodioAddressComponents, TypedDict):  # pylint:disable=inherit-non-class,too-few-public-methods
    """Dictionary returned by the Geocoder. Used only for typing."""
    latitude: float
    longitude: float
    formatted_address: str
    census_tract: str
    accuracy: float
    accuracy_type: str
    source: str
