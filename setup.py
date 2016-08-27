import os
from setuptools import setup

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "giphy-clip",
    version = "0.1",
    author = "Sphaerophoria",
    author_email = "sphaerophoria@gmail.com",
    description = ("Search/Preview some giphys and put them on your clipboard"
                                   "... all at the press of a button"),
    license = "BSD",
    keywords = "giphy gif clipboard copy paste",
    packages = ['giphy_clip'],
    scripts = ['bin/giphy-clip'],
    long_description=read('README'),
    install_requires=[
        'giphypop',
    ],
)
