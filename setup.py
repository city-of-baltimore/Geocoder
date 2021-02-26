from setuptools import setup, find_packages

setup(
    name="balt_geocoder",
    version="1.0.2",
    author="Brian Seel",
    author_email="brian.seel@baltimorecity.gov",
    description="(Baltimore City) Geocodio wrapper with address caching and Baltimore City specific checks",
    packages=find_packages('src'),
    package_data={'balt_geocoder': ['py.typed'], },
    python_requires='>=3.0',
    package_dir={'': 'src'},
    install_requires=[
        'requests~=2.25.1',
        'tenacity~=6.3.1',
        'loguru~=0.5.3'
    ],
)
