"""Defines types used by Geocodio"""
from typing import Dict, List, Optional, Tuple, TypedDict, Union


class GeocodioAddressComponets(TypedDict):
    """Dictionary used in the address_component of Geocodio locations. Used only for typing."""
    number: str
    predirectional: str
    street: str
    suffix: str
    formatted_street: str
    city: str
    state: str
    zip: Optional[str]
    country: str


class GeocodioCoordinates(TypedDict):
    """Dictionary used as the coordnates in geocodio results. Used only for typing."""
    lat: float
    lng: float


class GeocodioLocation(TypedDict):
    """Dictionary used as the input and results in geocodio results. Used only for typing."""
    address_components: GeocodioAddressComponets
    formatted_address: str
    location: Optional[GeocodioCoordinates]
    accuracy: Optional[int]
    accuracy_type: Optional[str]
    source: Optional[str]


class GeocodioResult(TypedDict):
    """Dictionary used as the result to Geocodio queries. Used only for typing."""
    input: GeocodioLocation
    results: List[GeocodioLocation]


class GeocodeResult(TypedDict):
    """Dictionary returned by the Geocoder. Used only for typing."""
    latitude: Optional[float]
    longitude: Optional[float]
    street_address: Optional[str]
    street_num: Optional[str]
    street_name: Optional[str]
    city: Optional[str]
    state: Optional[str]
    zip: Optional[str]
    census_tract: Optional[str]


CachedGeoKeyRev = Tuple[float, float]
CachedGeoKeyForward = str
CachedGeoKey = Union[CachedGeoKeyRev, CachedGeoKeyForward]
CachedGeoType = Dict[CachedGeoKey, GeocodeResult]
