"""Defines types used by Geocodio"""
from typing import Dict, List, Optional, Tuple, TypedDict, Union


class GeocodioAddressComponets(TypedDict):  # pylint:disable=inherit-non-class,too-few-public-methods
    """Dictionary used in the address_component of Geocodio locations. Used only for typing."""
    number: str
    predirectional: str
    street: str
    suffix: str
    formatted_street: str
    city: str
    state: str
    zip: Optional[str]  # pylint:disable=unsubscriptable-object
    country: str


class GeocodioCoordinates(TypedDict):  # pylint:disable=inherit-non-class,too-few-public-methods
    """Dictionary used as the coordnates in geocodio results. Used only for typing."""
    lat: float
    lng: float


class GeocodioLocation(TypedDict):  # pylint:disable=inherit-non-class,too-few-public-methods
    """Dictionary used as the input and results in geocodio results. Used only for typing."""
    address_components: GeocodioAddressComponets
    formatted_address: str
    location: Optional[GeocodioCoordinates]  # pylint:disable=unsubscriptable-object
    accuracy: Optional[int]  # pylint:disable=unsubscriptable-object
    accuracy_type: Optional[str]  # pylint:disable=unsubscriptable-object
    source: Optional[str]  # pylint:disable=unsubscriptable-object


class GeocodioResult(TypedDict):  # pylint:disable=inherit-non-class,too-few-public-methods
    """Dictionary used as the result to Geocodio queries. Used only for typing."""
    input: GeocodioLocation
    results: List[GeocodioLocation]  # pylint:disable=unsubscriptable-object


class GeocodeResult(TypedDict):  # pylint:disable=inherit-non-class,too-few-public-methods
    """Dictionary returned by the Geocoder. Used only for typing."""
    latitude: Optional[float]  # pylint:disable=unsubscriptable-object
    longitude: Optional[float]  # pylint:disable=unsubscriptable-object
    street_address: Optional[str]  # pylint:disable=unsubscriptable-object
    street_num: Optional[str]  # pylint:disable=unsubscriptable-object
    street_name: Optional[str]  # pylint:disable=unsubscriptable-object
    city: Optional[str]  # pylint:disable=unsubscriptable-object
    state: Optional[str]  # pylint:disable=unsubscriptable-object
    zip: Optional[str]  # pylint:disable=unsubscriptable-object
    census_tract: Optional[str]  # pylint:disable=unsubscriptable-object


CachedGeoKeyRev = Tuple[float, float]  # pylint:disable=unsubscriptable-object,too-few-public-methods
CachedGeoKeyForward = str
CachedGeoKey = Union[CachedGeoKeyRev, CachedGeoKeyForward]  # pylint:disable=unsubscriptable-object
CachedGeoType = Dict[CachedGeoKey, GeocodeResult]  # pylint:disable=unsubscriptable-object
