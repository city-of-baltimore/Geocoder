# Baltimore City Geocoder (bcgeocoder)
Wrapper that handles lookups for geocod.io. There is some extra logic to handle caching, to keep the number of lookups down. Also, some logic to make sure the results are in Baltimore City, since thats what we care about. 

Usage:

    from bcgeocoder import Geocoder
    gc = Geocoder(['apikey1', 'apikey2', ...])
    res = gc.reverse_geocode(39.28, 76.59)
