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

import json


def scrape_all():
    """
    Runs all scrapers

    returns:
        str: A json string containing the data from each scraper
    """
    data = dict()
    data['calendar_data'] = CalendarScraper().scrape()
    data['club_scraper'] = ClubScraper().scrape()
    data['course_scraper'] = CourseScraper().scrape()
    data['schedules_scraper'] = SchedulesScraper().scrape()
    return json.dumps(data)


if __name__=='__main__':
    scrape_all()