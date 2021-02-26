"""Constants used in some of the test suites"""
test_get_geocode_result_const = {
    'result': [
        {
            'address_components':
                {
                    'number': '1309',
                    'predirectional': 'N',
                    'street': 'Charles',
                    'suffix': 'St',
                    'formatted_street': 'N Charles St',
                    'city': 'Baltimore',
                    'county': 'Baltimore city',
                    'state': 'MD',
                    'zip': '21202',
                    'country': 'US'
                },
            'formatted_address': '1309 N Charles St, Baltimore, MD 21202',
            'location':
                {
                    'lat': 39.305076, 'lng': -76.615854
                },
            'accuracy': 1,
            'accuracy_type': 'rooftop',
            'source': 'Statewide',
            'fields':
                {
                    'census':
                        {
                            '2019':
                                {
                                    'census_year': 2019,
                                    'state_fips': '24',
                                    'county_fips': '24510',
                                    'tract_code': '110200',
                                    'block_code': '1025',
                                    'block_group': '1',
                                    'full_fips': '245101102001025',
                                    'place':
                                        {
                                            'name': 'Baltimore', 'fips': '2404000'
                                        },
                                    'metro_micro_statistical_area':
                                        {
                                            'name': 'Baltimore-Columbia-Towson, MD',
                                            'area_code': '12580',
                                            'type': 'metropolitan'
                                        },
                                    'combined_statistical_area':
                                        {
                                            'name': 'Washington-Baltimore-Arlington, DC-MD-VA-WV-PA',
                                            'area_code': '548'
                                        },
                                    'metropolitan_division': None,
                                    'source': 'US Census Bureau'
                                }
                        }
                }
        },
        {
            'address_components':
                {
                    'number': '1319',
                    'predirectional': 'N',
                    'street': 'Charles',
                    'suffix': 'St',
                    'formatted_street': 'N Charles St',
                    'city': 'Baltimore',
                    'county': 'Baltimore city',
                    'state': 'MD',
                    'zip': '21202',
                    'country': 'US'
                },
            'formatted_address': '1319 N Charles St, Baltimore, MD 21202',
            'location':
                {
                    'lat': 39.305241, 'lng': -76.615862
                },
            'accuracy': 1,
            'accuracy_type': 'rooftop',
            'source': 'Statewide',
            'fields':
                {
                    'census':
                        {
                            '2019':
                                {
                                    'census_year': 2019,
                                    'state_fips': '24',
                                    'county_fips': '24510',
                                    'tract_code': '110200',
                                    'block_code': '1025',
                                    'block_group': '1',
                                    'full_fips': '245101102001025',
                                    'place':
                                        {
                                            'name': 'Baltimore', 'fips': '2404000'
                                        },
                                    'metro_micro_statistical_area':
                                        {
                                            'name': 'Baltimore-Columbia-Towson, MD',
                                            'area_code': '12580',
                                            'type': 'metropolitan'
                                        },
                                    'combined_statistical_area':
                                        {
                                            'name': 'Washington-Baltimore-Arlington, DC-MD-VA-WV-PA',
                                            'area_code': '548'
                                        },
                                    'metropolitan_division': None,
                                    'source': 'US Census Bureau'
                                }
                        }
                }
        }]}

# verification data for test_get_geocode_result
geocode_result_data = {
    'latitude': 39.305076,
    'longitude': -76.615854,
    'number': '1309',
    'predirectional': 'N',
    'street': 'Charles',
    'suffix': 'St',
    'formatted_street': 'N Charles St',
    'city': 'Baltimore',
    'county': 'Baltimore city',
    'state': 'MD',
    'zip': '21202',
    'country': 'US',
    'formatted_address': '1309 N Charles St, Baltimore, MD 21202',
    'census_tract': '110200',
    'accuracy': 1.0,
    'accuracy_type': 'rooftop',
    'source': 'Statewide',
}

geocode_rev_result_data = {
    'latitude': 39.305076,
    'longitude': -76.615854,
    'number': '1309',
    'predirectional': 'N',
    'street': 'Charles',
    'suffix': 'St',
    'formatted_street': 'N Charles St',
    'city': 'Baltimore',
    'county': 'Baltimore city',
    'state': 'MD',
    'zip': '21201',
    'country': 'US',
    'formatted_address': '1309 N Charles St, Baltimore, MD 21201',
    'census_tract': '110200',
    'accuracy': 1.0,
    'accuracy_type': 'rooftop',
    'source': 'Statewide',
}

# verification for test_geocode_bad_characters
geocode_bad_characters = {
    'latitude': 39.369861,
    'longitude': -76.651934,
    'formatted_address': 'I-83, Baltimore, MD 21202',
    'accuracy': 0.6,
    'accuracy_type': 'street_center',
    'source': 'TIGER/Line® dataset from the US Census Bureau', 'number': '',
    'predirectional': '',
    'street': 'I-83',
    'suffix': '',
    'formatted_street': 'I-83',
    'city': 'Baltimore',
    'county': 'Baltimore city',
    'state': 'MD',
    'zip': '21202',
    'country': 'US',
    'census_tract': '271501'
}

# complete dummy data
test_geocode_result = {
    'latitude': 66.66,
    'longitude': 77.77,
    'number': '0000',
    'predirectional': 'N',
    'street': 'TESTSTREET',
    'suffix': 'DR',
    'formatted_street': 'TESTSTREETADDRESS',
    'city': 'TESTCITY',
    'county': 'TESTCOUNTY',
    'state': 'TESTSTATE',
    'zip': 'TESTZIP',
    'country': 'TESTCOUNTRY',
    'formatted_address': 'TESTFORMATTEDADDRESS',
    'census_tract': 'TESTCENUSTRACT',
    'accuracy': .5,
    'accuracy_type': 'guess',
    'source': 'test'
}

# updated dummy data for test_update_cached_geo
test_update_cached_geo_data = {
    'latitude': 66.66,
    'longitude': 77.77,
    'number': '0000',
    'predirectional': 'N',
    'street': 'TESTSTREET',
    'suffix': 'DR',
    'formatted_street': 'UPDATED',
    'city': 'TESTCITY',
    'county': 'TESTCOUNTY',
    'state': 'TESTSTATE',
    'zip': 'TESTZIP',
    'country': 'TESTCOUNTRY',
    'formatted_address': 'TESTFORMATTEDADDRESS',
    'census_tract': 'TESTCENUSTRACT',
    'accuracy': 1.0,
    'accuracy_type': 'guess',
    'source': 'test'
}
