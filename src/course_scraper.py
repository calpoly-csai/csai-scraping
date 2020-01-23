"""
Title: Course Scraper Class
Author: Cameron Toy
Date: 1/22/2020
Organization: Cal Poly CSAI
Description: Scrapes course data from the Cal Poly website
"""

import scraper_base
import pandas as pd


class CourseScraper:

    def __init__(self):
        pass

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
        if all_departments:
            top_link = "http://catalog.calpoly.edu/coursesaz/"
            top_soup = scraper_base.get_soup(top_link, ver=False)
            # Changed scraping method because source for visible links changed, but
            # old links are still in the source and cause some 404 errors
            departments_az = top_soup.find('table')
            department_urls = [department.get('href')
                               for department in departments_az.find_all('a')
                               if department.get('href')]
        else:
            department_urls = ['/coursesaz/csc/', '/coursesaz/cpe/']

        scraped_courses = []

        # Retrieves course info for each department
        for department in department_urls:
            # Extracts the department name from the URL
            dep_name = (department.rsplit('/', 2)[1]).upper()

            # Gets raw list of courses and info for department
            dep_link = 'http://catalog.calpoly.edu' + department
            dep_soup = scraper_base.get_soup(dep_link)
            courses = dep_soup.findAll("div", {"class": "courseblock"})

            for course in courses:
                course_name_and_units = (course.find ("p", {"class": "courseblocktitle"})).get_text()
                course_name, course_units = course_name_and_units.splitlines()
                course_units = course_units.split(' ', 1)[0]

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
                            except IndexError:
                                pass
                            section = 'prereq'
                        elif word.endswith('Corequisite:'):
                            try:
                                course_terms.append((word.split('Cor'))[0])
                            except IndexError:
                                pass
                            section = 'coreq'
                        elif word.endswith('Concurrent:'):
                            try:
                                course_terms.append((word.split('Con'))[0])
                            except IndexError:
                                pass
                            section = 'conc'
                        elif word.endswith('Recommended:'):
                            try:
                                course_terms.append((word.split('Rec'))[0])
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

                maybe_join = (lambda x: ' '.join(x) if x else 'NA')
                course_prereqs = maybe_join(course_prereqs)
                course_coreqs = maybe_join(course_coreqs)
                course_conc = maybe_join(course_conc)
                course_rec = maybe_join(course_rec)
                course_terms = maybe_join(course_terms)

                document = {
                    "DEPARTMENT": dep_name,
                    "COURSE_NAME": course_name,
                    "UNITS": course_units,
                    "PREREQUISITES": course_prereqs,
                    "COREQUISITES": course_coreqs,
                    "CONCURRENT": course_conc,
                    "RECOMMENDED": course_rec,
                    "TERMS_TYPICALLY_OFFERED": course_terms
                }

                scraped_courses.append(document)

        return pd.DataFrame(scraped_courses).to_csv(None, index=False)

