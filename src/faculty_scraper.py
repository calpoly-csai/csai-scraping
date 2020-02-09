"""
Title: Faculty Scraper Class
Author: Cameron Toy
Date: 1/22/2020
Organization: Cal Poly CSAI
Description: Scrapes faculty data from the Cal Poly website. Mostly redundant because
of schedules_scraper.py. Only unique information scraped is research interests.
"""

import scraper_base
from time import sleep
import pandas as pd


class FacultyScraper:

    def __init__(self):
        self.REST_TIME = 100  # Time between requests in ms
        self.CSC_TOP_LINK = "https://csc.calpoly.edu/faculty/"
        self.CPE_TOP_LINK = "https://cpe.calpoly.edu/faculty/"

    def parse_single_employee(self, url):
        """
        Scrapes data from a single Cal Poly employee.

        args:
            url (str)

        returns:
            dict(str:str)
        """

        # Due to certificate issues with CSC employee pages, verification
        # is turned off for requests in the scraper module. This leads to
        # lots of warning during runtime but unaffected data.
        soup = scraper_base.get_soup(url, ver=False)
        name = soup.find("h1").text
        office = 'NA'
        email = 'NA'
        phone = 'NA'
        research_interests = 'NA'

        # Information is stored in different blocks for staff and faculty
        if url.rsplit("/", 3)[1] == "staff":
            main_info_text = [l.text for l in soup.find_all("span")]
            table = soup.find("table")
        else:
            faculty_main_info = soup.find(id="facultyMainBlock")
            table = faculty_main_info.find("table")
            main_info_text = faculty_main_info.text.splitlines()

            # Getting the research interests for every professor
            # Doesn't work for Hasmik Gharibyan and other people who have a biography
            faculty_additional_info = soup.find(class_="facultyBlock")
            if faculty_additional_info is not None and faculty_additional_info.span:
                research_interests = []
                for string in faculty_additional_info.stripped_strings:
                    research_interests.append(string)

        found_office = found_phone = found_email = False

        for line in main_info_text:
            if not found_office:
                if line.startswith("Office:"):
                    office = line.rsplit(" ", 1)[1]
                    found_office = True
            if not found_phone:
                if line.startswith("Phone "):
                    phone = line.rsplit(" ", 1)[1]
                    found_phone = True
            if not found_email:
                if line.startswith("Email:"):
                    # For faculty pages, the character following "Email:" is not a space but \xa0
                    try:
                        first_split = line.split("\xa0", 1)[1]
                    except IndexError:
                        first_split = line.split(" ", 1)[1]
                    email = first_split.split("(", 1)[0] + "@calpoly.edu"
            if found_office and found_phone and found_email:
                break

        # office_hours = dict()

        # Office hour parsing is currently disabled. The previous solution only worked for the CPE department
        # and stored office hours in a dictionary, which is not represented in a CSV file. A separate source
        # of office hours should replace this.
        # #
        # # This method DOES NOT parse office hours for staff, whose office hours are single-line formatted
        # # like: "Mon - Fri: 10:00 am to 5:00 pm". Additional parsing will have to be added for them. For now, their
        # # office hours will show up as 'NA'
        # try:
        #     rows = table.find_all("tr")
        # except AttributeError:
        #     # Best way to represent no office hours? Currently using 'NA' as a string
        #     office_hours = "NA"
        # else:
        #     rows.pop(0)  # Don't need header row
        #     for row in rows:
        #         col = row.find_all("td")
        #         days = (
        #             col[0].text.replace(",", "").split()
        #         )  # Turns "Monday, Wednesday" into ['Monday', 'Wednesday']
        #         time = col[1].text
        #         room = col[2].text
        #         for day in days:
        #             office_hours[day] = dict()
        #             office_hours[day]["time"] = time
        #             office_hours[day]["room"] = room

        faculty_info = {
            "NAME": name,
            "OFFICE": office,
            "EMAIL": email,
            "PHONE": phone,
            "RESEARCH_INTERESTS": research_interests,
        }

        return faculty_info


    def scrape(self):
        """
        Scrapes data from all CPE and CSC employees

        args:
        no_upload (Bool): Used by scraper.py to control uploading vs just returning
            scraped data

        returns:
            str: A CSV string of scraped data
        """
        scraped_faculty = []

        # Verification turned off; read main note in self.parse_single_employee
        soup = scraper_base.get_soup(self.CSC_TOP_LINK, ver=False)
        for link in soup.find_all("a", href=True):
            nav = link["href"]
            if (nav.startswith("/faculty/") or nav.startswith("/staff")) and (nav != "/faculty/" and nav != "/staff/"):
                info = self.parse_single_employee("https://csc.calpoly.edu" + nav)
                scraped_faculty.append(info)
                sleep(self.REST_TIME / 1000)

        soup = scraper_base.get_soup(self.CPE_TOP_LINK)
        for link in soup.find_all("a", href=True):
            nav = link["href"]
            if (nav.startswith("/faculty/") or nav.startswith("/staff")) and (nav != "/faculty/" and nav != "/staff/"):
                info = self.parse_single_employee("https://cpe.calpoly.edu" + nav)
                scraped_faculty.append(info)
                sleep(self.REST_TIME / 1000)

        return pd.DataFrame(scraped_faculty).to_csv(None, index=False)
