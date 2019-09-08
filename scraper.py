import requests
from bs4 import BeautifulSoup
from timeit import default_timer as timer


# TODO: Add support for user agent headers
def get_soup(url, to=10):
    """
    Turns a URL into a parsed BeautifulSoup object and
    raises exceptions for scraping modules

    args:
    url (String): URL to parse
    to (Num): Time before timeout in seconds
    """
    r = requests.get(url, timeout=to)
    r.raise_for_status()
    return BeautifulSoup(r.text, 'html.parser')


# TODO: Add support for email error logging/reporting
def scraper(func):
    """
    Wraps each scraper function to include uploading, error handling,
    testing, and timing.
    """

    def wrapper(*args, **kwargs):
        self = args[0]
        try:
            start = timer()
            data = func(*args, **kwargs)
            end = timer()
        # Catches all exceptions raised by requests
        except requests.exceptions.RequestException as e:
            print(e)
        else:
            print(f'Scraped {data[0].document_type}s in {end - start} seconds.')
            if kwargs['no_upload']:
                return data
            else:
                self.firebase_proxy.batched_write(data)

    return wrapper
