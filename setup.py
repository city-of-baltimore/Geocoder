import setuptools

setuptools.setup(
    name="bcgeocoder",
    version="0.1",
    author="Brian Seel",
    author_email="brian.seel@baltimorecity.gov",
    description="(Baltimore City) Geocodio wrapper with address caching and Baltimore City specific checks",
    packages=setuptools.find_packages(),
    package_data={'bcgeocoder': ['py.typed'],},
    python_requires='>=3.0',
    install_requires=[
        'requests',
        'retrying',
    ],
)
