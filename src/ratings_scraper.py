"""
Title: Cal Poly Ratings Scraper Class
Author: Cameron Toy
Date: 2/9/2020
Organization: Cal Poly CSAI
Description: Scrapes professor ratings from calpolyratings.com
"""

# Only finds a rating and difficulty when a professor has an average rating on their page.
# Doesn't compute average rating/difficulty from reviews

import scraper_base
from barometer import barometer, DEBUG, SUCCESS, ALERT, INFO, NOTICE, WARNING
import requests
import pandas as pd
from time import sleep


class RatingsScraper:

    def __init__(self):
        self.TOP_LINK = 'https://calpolyratings.com'
        self.REST_TIME = 200  # Time between requests in ms

    @barometer
    def scrape(self):
        data = []
        print(DEBUG, f"Starting calpolyratings scrape: TOP_LINK={self.TOP_LINK}, REST_TIME={self.REST_TIME}ms")
        page_num = 1
        while True:
            try:
                soup = scraper_base.get_soup(f"{self.TOP_LINK}/?page={page_num}")
            except requests.exceptions.RequestException as e:
                # Keep trying to get new pages until 404. On 404, return existing data
                if str(e).startswith('404 Client Error'):
                    print(NOTICE, f"Page {page_num} not found. Ending scrape")
                    print(SUCCESS, f"Done! Scraped ratings for {len(data)} professors")
                    return pd.DataFrame(data).to_csv(None, index=False)
                print(ALERT, e)
                return None
            else:
                print(SUCCESS, f"Retrieved page {page_num}")
                page_num += 1
                links = (a['href'] for a in soup.find_all('a', href=True))
                prof_links = [a for a in links if a.startswith('/') and not a.endswith('/')]
                for prof in prof_links:
                    sleep(self.REST_TIME / 1000)
                    page = self.get_prof_page(prof)
                    if page:
                        data.append(page)

    def get_prof_page(self, extension):
        try:
            prof_page = scraper_base.get_soup(f"{self.TOP_LINK}{extension}")
        except requests.exceptions.RequestException as e:
            print(WARNING, f"Failed scraping {self.TOP_LINK}{extension}: {e}")
            return None
        else:
            print(DEBUG, f"Retrieved professor page from {self.TOP_LINK}{extension}")
            prof_name = prof_page.title.text.strip()
            # Why is all relevant data in a button block? I have no idea.
            main_block = prof_page.findAll('button')[2]
            prof_rating = main_block.find("span", {"class": "teacher-rating"}).text
            prof_difficulty = main_block.find("span", {"class": "evals-span"}).text
            if prof_difficulty:
                prof_difficulty = prof_difficulty.split()[1]
            p = {"NAME": prof_name,
                 "RATING": prof_rating,
                 "DIFFICULTY": prof_difficulty}
            return p

