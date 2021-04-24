# Baltimore City Geocoder (balt-geocoder)
Wrapper that handles lookups for geocod.io. There is some extra logic to handle caching, to keep the number of lookups down. Also, some logic to make sure the results are in Baltimore City, since thats what we care about. 

## Installation
`pip install balt-geocoder`

## API Setup
Sign up for a [Geocodio](https://www.geocod.io/) account and follow the instructions under *API Keys* 

## Usage

    from balt_geocoder import Geocoder
    gc = Geocoder(['apikey1', 'apikey2', ...])
    gc_output = gc.geocode('100 Holliday St, Baltimore, MD')
    reverse_gc_output = gc.reverse_geocode(39.28, 76.59)

# Testing
To run tests, run `tox -- --apikey <GEOCOODIO API KEY>`
