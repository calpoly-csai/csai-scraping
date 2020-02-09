"""
Title: Scraper base
Author: Cameron Toy
Date: 1/22/2020
Organization: Cal Poly CSAI
Description: Stores functions common to all Cal Poly scrapers
"""

import requests
from bs4 import BeautifulSoup


# TODO: Add support for user agent headers
def get_soup(url, ver=True, to=30):
    """
    Turns a URL into a parsed BeautifulSoup object and
    raises exceptions for scraping modules

    args:
        url (str): URL to parse
        ver (bool): Skips certificate verification when set to False
        to (num): Number of seconds until request timeout
    """
    r = requests.get(url, verify=ver, timeout=to)
    r.raise_for_status()
    # lxml used for speed
    return BeautifulSoup(r.text, 'lxml')