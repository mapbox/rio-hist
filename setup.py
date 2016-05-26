import os
import sys
from setuptools import setup, find_packages
from setuptools.extension import Extension

# Parse the version from the fiona module.
with open('rio_hist/__init__.py') as f:
    for line in f:
        if line.find("__version__") >= 0:
            version = line.split("=")[1].strip()
            version = version.strip('"')
            version = version.strip("'")
            break

long_description = """Histogram matching plugin for rasterio.

See https://github.com/mapbox/rio-hist for docs."""


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(name='rio-hist',
      version=version,
      description=u"Histogram matching plugin for rasterio",
      long_description=long_description,
      classifiers=[],
      keywords='',
      author=u"Matthew Perry",
      author_email='perry@mapbox.com',
      url='https://github.com/mapbox/rio-hist',
      license='BSD',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=["click", "rasterio", "rio_color>=0.4"],
      extras_require={
          'plot': ['matplotlib'],
          'test': ['pytest', 'pytest-cov', 'codecov']},
      entry_points="""
      [rasterio.rio_plugins]
      hist=rio_hist.scripts.cli:hist
      """
      )
