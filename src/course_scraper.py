"""
Title: Course Scraper Class
Author: Cameron Toy
Date: 1/22/2020
Organization: Cal Poly CSAI
Description: Scrapes course data from the Cal Poly website
"""

# Added course descriptions

import requests
from barometer import barometer, SUCCESS, ALERT, INFO, DEBUG
import scraper_base
import pandas as pd
from time import sleep
import re


class CourseScraper:

    def __init__(self):
        self.REST_TIME = 100

    @barometer
    def scrape(self, all_departments=False):
        """
        Scrapes course information and requirements to CSV

        args:
            all_departments (bool): Scrapes all departments if True, or just CPE
            and CSC if False (default False)

        returns:
            str: A CSV string of scraped data
        """
        # Retrieves department list from Cal Poly
        print(DEBUG, f"Starting course scrape: all_departments={all_departments}, REST_TIME={self.REST_TIME}")
        print(INFO, "Starting course scrape")
        if all_departments:
            top_link = "http://catalog.calpoly.edu/coursesaz/"
            print(INFO, f"Starting scrape on {top_link}")
            try:
                top_soup = scraper_base.get_soup(top_link, ver=False)
            except requests.exceptions.RequestException as e:
                print(ALERT, e)
                return None
            print(SUCCESS, "Retrieved top-level courses page")
            # Changed scraping method because source for visible links changed, but
            # old links are still in the source and cause some 404 errors
            departments_az = top_soup.find('table')
            department_urls = [department.get('href')
                               for department in departments_az.find_all('a')
                               if department.get('href')]
            if not department_urls:
                print(ALERT, "Couldn't find departments list. Aborting scrape.")
                return None
            print(INFO, f"Found URLs for {len(department_urls)} departments")
        else:
            print(INFO, "Just scraping CSC and CPE courses")
            department_urls = ['/coursesaz/csc/', '/coursesaz/cpe/']

        scraped_courses = []

        # Retrieves course info for each department
        for department in department_urls:
            # Extracts the department name from the URL
            dep_name = (department.rsplit('/', 2)[1]).upper()
            # Gets raw list of courses and info for department
            dep_link = 'http://catalog.calpoly.edu' + department
            try:
                dep_soup = scraper_base.get_soup(dep_link)
                sleep(self.REST_TIME / 1000)
            except requests.exceptions.RequestException as e:
                print(ALERT, e)
                return None
            print(SUCCESS, f"Retrieved {dep_name} courses from {dep_link}")
            courses = dep_soup.findAll("div", {"class": "courseblock"})
            print(DEBUG, f"Found {len(courses)} courses")
            for course in courses:
                course_name_and_units = (course.find("p", {"class": "courseblocktitle"})).get_text()
                course_name, course_units = course_name_and_units.splitlines()
                print(DEBUG, f"Found {course_name}")
                course_units = course_units.split(' ', 1)[0]
                paragraphs = course.findAll('p')
                if len(paragraphs) == 5:
                    ge_areas = re.findall(r'Area (\w+)', paragraphs[1].text)
                else:
                    ge_areas = None
                course_desc = paragraphs[-1].text
                course_terms_and_reqs = (course.find("div", {"class": "noindent courseextendedwrap"})).get_text()

                section = None
                course_prereqs, course_coreqs, course_conc, course_rec, course_terms = [], [], [], [], []
                for word in course_terms_and_reqs.split():
                    if word.endswith(':'):
                        if word == 'Offered:':
                            section = 'terms'
                        # Last term (F,W,SP, etc) will be appended to the front of "Prerequisite:" or whatever category
                        # comes immediately after terms offered, so "str.endswith(blah)" has to be done instead
                        # of "str == blah"
                        elif word.endswith('Prerequisite:'):
                            try:
                                course_terms.append((word.split('Pre'))[0])
                                print(DEBUG, "Found prerequisites")
                            except IndexError:
                                pass
                            section = 'prereq'
                        elif word.endswith('Corequisite:'):
                            try:
                                course_terms.append((word.split('Cor'))[0])
                                print(DEBUG, "Found corequisites")
                            except IndexError:
                                pass
                            section = 'coreq'
                        elif word.endswith('Concurrent:'):
                            try:
                                course_terms.append((word.split('Con'))[0])
                                print(DEBUG, "Found concurrent courses")
                            except IndexError:
                                pass
                            section = 'conc'
                        elif word.endswith('Recommended:'):
                            try:
                                course_terms.append((word.split('Rec'))[0])
                                print(DEBUG, "Found recommended courses")
                            except IndexError:
                                pass
                            section = 'rec'
                        else:
                            pass

                    else:
                        if section == 'prereq':
                            course_prereqs.append(word)
                        elif section == 'coreq':
                            course_coreqs.append(word)
                        elif section == 'conc':
                            course_conc.append(word)
                        elif section == 'rec':
                            course_rec.append(word)
                        elif section == 'terms':
                            course_terms.append(word)
                        else:
                            pass

                # Update: Now joined with a comma
                maybe_join = (lambda x: ','.join(x) if x else 'NA')
                course_prereqs = maybe_join(course_prereqs)
                course_coreqs = maybe_join(course_coreqs)
                course_conc = maybe_join(course_conc)
                course_rec = maybe_join(course_rec)
                course_terms = maybe_join(course_terms)
                ge_areas = maybe_join(ge_areas)

                document = {
                    "DEPARTMENT": dep_name,
                    "COURSE_NAME": course_name,
                    "UNITS": course_units,
                    "PREREQUISITES": course_prereqs,
                    "COREQUISITES": course_coreqs,
                    "CONCURRENT": course_conc,
                    "RECOMMENDED": course_rec,
                    "TERMS_TYPICALLY_OFFERED": course_terms,
                    "GE_AREAS": ge_areas,
                    "COURSE_DESC": course_desc
                }

                scraped_courses.append(document)
        print(SUCCESS, f"Done! Scraped {len(scraped_courses)} courses")
        return pd.DataFrame(scraped_courses).to_csv(None, index=False)


