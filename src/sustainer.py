"""
Title: Scraper sustainer
Author: Cameron Toy
Date: 1/22/2020
Organization: Cal Poly CSAI
Description: Runs all scrapers and stores the data in a JSON string
"""

from calendar_scraper import CalendarScraper
from club_scraper import ClubScraper
from course_scraper import CourseScraper
from schedules_scraper import SchedulesScraper
from location_scraper import LocationScraper

import datetime
import json


def scrape_all(filename, log_level=8, verbosity=8):
    """
    Runs all scrapers

    returns:
        str: A json string containing the data from each scraper
    """
    data = dict()
    data['calendar_data'] = CalendarScraper().scrape(logfile=filename, log_level=log_level, verbosity=verbosity)
    data['club_scraper'] = ClubScraper().scrape(logfile=filename, log_level=log_level, verbosity=verbosity)
    data['course_scraper'] = CourseScraper().scrape(logfile=filename, log_level=log_level, verbosity=verbosity)
    data['schedules_scraper'] = SchedulesScraper().scrape(logfile=filename, log_level=log_level, verbosity=verbosity)
    data['location_scraper'] = LocationScraper().scrape(logfile=filename, log_level=log_level, verbosity=verbosity)
    return json.dumps(data)


if __name__=='__main__':
    now = datetime.datetime.now()
    filename = f'{now.strftime("%Y-%m-%d")}.txt'
    data = scrape_all(filename)
    with open('data.json', 'w') as d:
        d.write(data)
