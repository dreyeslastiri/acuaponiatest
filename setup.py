###TODO: install twine (pip install twine)
###TODO: url

from distutils.core import setup
# Help: https://docs.python.org/3.1/distutils/apiref.html#distutils.core.setup
setup(
    name = "acuaponiatest",
    packages = ["models","_pint_dimensions"],
    version = "2018.01", #look for python versioneer, used by e.g. pandas
    description = "Dynamic models for aquaponics",
    author = "Daniel Reyes Lastiri",
    author_email = "d.reyeslastiri@yandex.com",	
    url = "http://chardet.feedparser.org/", #update
    download_url = "http://chardet.feedparser.org/download/python3-chardet-1.0.1.tgz", #update
    license = 'GPLv3',
    keywords = ["aquaponics", "modelling", "simulation"],
    classifiers = [
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Development Status :: 1 - Planning",
        "Environment :: Console",
        "Intended Audience :: Developers",
	"Intended Audience :: End Users/Desktop", #Is it as in GUI?
	"Intended Audience :: Science/Research",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
	"Natural Language :: English",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering",
	"Topic :: Scientific/Engineering :: Mathematics"
        ],
    install_requires = [
	"numpy>=1.13.0",
	"scipy>=0.19.1",
	"pandas>=0.20.3",
	"matplotlib>=2.0.2",
	"pint>=0.7.2"
	],
    python_requires = ">=3",
    data_files = [('$HOME/.config/matplotlib', ['setupdata/acuaplotsrc1.mplstyle'])],
    long_description = """\
Dynamic models for aquaponics
-----------------------------

Components
 - Fish tank: Fish growth & excretion, Fish feeder, and Fish tank
 - Mechanical filter: Drum filter
 - ...

This version requires Python 3 or later
"""
)