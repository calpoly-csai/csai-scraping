"""
Title: Calendar Scraper Class
Author: Cameron Toy
Date: 1/22/2020
Organization: Cal Poly CSAI
Description: Scrapes calendar data from the main Cal Poly academic calendar
"""

import scraper_base
import requests # needed for HTTPError, even with scraper_base
import calendar as cal
import pandas as pd


class CalendarScraper:

    def __init__(self):
        self.CALENDAR_EPOCH = 2018
        self.TOP_LINK = 'https://registrar.calpoly.edu'
        self.months = list(cal.month_name)

    def month_lengths(self, year):
        """
        args:
            year (int): year whose month lengths will be returned

        returns:
            list(int): 1-indexed list of month length for the given year
        """
        return [''] + [cal.monthrange(year, i)[1] for i in range(1,13)]


    def parse_dates(self, dates, year):
        """
        Turns date strings into formatted dictionaries

        args:
            dates (str): Date range
            year (int): Year dates occur in

        returns:
            dict(str : list(int)) : A dictionary mapping each month in the date
                range to its days

        examples:
            'March 30 - April 3' -> {'March': [30, 31], 'April': [1, 2, 3]}
            'January 25' -> {'January': [25]}
            'February 2 - 7' -> {'February': [2, 3, 4, 5, 6, 7]}
        """
        month_lengths = self.month_lengths(year)
        tokens = [t for t in dates.split() if t != '-']
        parsed_dates = dict()

        if len(tokens) == 2:
            month, day = tokens
            parsed_dates[month] = [int(day)]
        elif len(tokens) == 3:
            month, start, end = tokens
            parsed_dates[month] = [n for n in range(int(start), int(end) + 1)]
        elif len(tokens) == 4:
            month_1, day_1, month_2, day_2 = tokens
            i = self.months.index(month_1)
            num_days = month_lengths[i]
            parsed_dates[month_1] = [n for n in range(int(day_1), num_days + 1)]
            parsed_dates[month_2] = [n for n in range(1, int(day_2) + 1)]

        return parsed_dates

    def make_date(self, month, day, year):
        """
        args:
            month (str)
            day (int)
            year (int)
        returns:
            str: month_day_year
        """
        return f'{self.months.index(month)}_{day}_{year}'

    def scrape(self):
        """
        Scrapes academic calendar data to CSV

        returns:
            str: A CSV string of scraped data
        """
        starting_year = self.CALENDAR_EPOCH
        calendar = dict()

        while True:
            ending_year = starting_year + 1
            current_year = starting_year
            calendar_url = f'{self.TOP_LINK}/{starting_year}-{ending_year - 2000}-academic-calendar'

            try:
                calendar_soup = scraper_base.get_soup(calendar_url)
            # Returns on an invalid school year; should always return.
            except requests.exceptions.HTTPError:
                dates = list(calendar.values())
                return pd.DataFrame(dates).to_csv(None, index=False)
            else:
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
                        parsed_dates = self.parse_dates(dates, current_year)
                        # Ugly solution to change the calendar year during the school year.
                        # Assumes there will always be an event in January.
                        if 'January' in parsed_dates and current_year != ending_year:
                            current_year = ending_year
                        # Second column is just the days of the week; ignore
                        events = [t.strip() for t in cols[2].text.splitlines()]
                        for month, days in parsed_dates.items():
                            for day in days:
                                date = self.make_date(month, day, current_year)
                                if date in calendar:
                                    calendar[date]['EVENTS'].extend(events)
                                else:
                                    entry = dict()
                                    entry['DATE'] = date
                                    entry['DAY'] = day
                                    entry['MONTH'] = month
                                    entry['YEAR'] = current_year
                                    entry['EVENTS'] = events
                                    calendar[date] = entry

                starting_year += 1
