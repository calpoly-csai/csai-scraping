# TODO: Integrate scraping of other Cal Poly calendars besides the academic calendar

import requests
import scraper
from firebase.firebase_proxy import FirebaseProxy
from transaction import Transaction


class CalendarScraper:

    def __init__(self, firebase_proxy: FirebaseProxy):
        self.firebase_proxy = firebase_proxy

        self.COLLECTION = 'Scraped'
        self.DOCUMENT_TYPE = 'calendar'
        self.CALENDAR_EPOCH = 2018
        self.TOP_LINK = 'https://registrar.calpoly.edu'
        self.month_lengths = {
            'January': 31,
            'February': None,  # defined in parse_dates
            'March': 31,
            'April': 30,
            'May': 31,
            'June': 30,
            'July': 31,
            'August': 31,
            'September': 30,
            'October': 31,
            'November': 30,
            'December': 31
        }

    # Turns 'March 30 - April 3' into
    # {'March': [30, 31], 'April': [1, 2, 3]}
    # or 'January 11 - 16' into
    # {'January': [11, 12, 13, 14, 15, 16]}
    def parse_dates(self, dates, is_leap=False):
        """
        Turns date strings into formatted dictionaries

        examples:
        'March 30 - April 3' -> {'March': [30, 31], 'April': [1, 2, 3]}
        'January 25' -> {'January': [25]}
        'February 2 - 7' -> {'February': [2, 3, 4, 5, 6, 7]}
        """
        self.month_lengths['February'] = 29 if is_leap else 28
        is_month = (lambda x: not x.isnumeric())
        tokens = [t for t in dates.split()
                  if t != '-']
        parsed_dates = dict()
        second_month = False
        active_month = None
        starting_date = None

        for t in tokens:
            if is_month(t):
                if active_month:
                    second_month = True
                    parsed_dates[active_month] = ([n for n in range(
                        starting_date, self.month_lengths[active_month] + 1
                    )])
                active_month = t
            elif not starting_date:
                starting_date = int(t)
            elif second_month:
                parsed_dates[active_month] = [n for n in range(
                    1, int(t) + 1
                )]
                starting_date = None
            else:  # There is a second date after the dash
                parsed_dates[active_month] = [n for n in range(
                    starting_date, int(t) + 1
                )]
                starting_date = None

        if starting_date:
            parsed_dates[active_month] = [starting_date]

        return parsed_dates

    @scraper.scraper
    def scrape(self, no_upload=False):
        """
        Scrapes academic calendar data to Firebase

        args:
        no_upload (Bool): Used by scraper.py to control uploading vs just returning
            scraped data

        returns:
        [Transaction]: A list containing a single Transaction object with
            the scraped calendar data
        """
        starting_year = self.CALENDAR_EPOCH
        calendar = dict()
        calendar[self.CALENDAR_EPOCH] = dict()

        # Returns on an invalid school year; should always return.
        while True:
            ending_year = starting_year + 1
            current_year = starting_year
            is_leap = True if current_year % 4 == 0 else False
            calendar_url = self.TOP_LINK + '/' + str(starting_year) + '-' + str(ending_year - 2000) + '-academic-calendar'

            try:
                calendar_soup = scraper.get_soup(calendar_url, to=20)
            except requests.exceptions.HTTPError:
                return [Transaction(self.COLLECTION,
                                    'calendar',
                                    calendar,
                                    self.DOCUMENT_TYPE)]
            else:
                calendar[ending_year] = dict()
                # Finds all tables on the page (summer/fall/winter/spring quarters)
                # Excludes the last summary table.
                # Note: summary table id has a space at the end. All years are like this.
                tables = calendar_soup.find_all(lambda tag:
                                                tag.name == 'table'
                                                and tag.has_attr('id')
                                                and tag['id'] != "SUMMARY OF CALENDAR DAYS ")
                for table in tables:
                    for row in table.find_all('tr'):
                        cols = row.find_all('td')
                        dates = cols[0].text
                        parsed_dates = self.parse_dates(dates, is_leap)
                        # Ugly solution to change the calendar year during the school year.
                        # Assumes there will always be an event in January.
                        if 'January' in parsed_dates and current_year != ending_year:
                            current_year = ending_year
                            is_leap = True if current_year % 4 == 0 else False
                        # Second column is just the days of the week; ignore
                        events = [t.strip() for t
                                  in cols[2].text.splitlines()]
                        for month, days in parsed_dates.items():
                            if month not in calendar[current_year]:
                                calendar[current_year][month] = dict()
                            for day in days:
                                try:
                                    bool(calendar[current_year][month][day])
                                except KeyError:
                                    calendar[current_year][month][day] = events
                                else:
                                    calendar[current_year][month][day].extend(events)

                starting_year += 1



