# Scrapes and logs course information for Cal Poly
# Made by Cameron Toy for Cal Poly Computer Science and Artificial Intelligence

import requests
from bs4 import BeautifulSoup

from firebase.firebase_proxy import FirebaseProxy
from transaction import Transaction



class CourseScraper:
    # Firestore client parameter must be named "firebase_proxy" for dependency
    # injection to work
    # (https://github.com/google/pinject#basic-dependency-injection)
    def __init__(self, firebase_proxy: FirebaseProxy):
        self.firebase_proxy = firebase_proxy

        # Collection where all scraped documents will go
        self.COLLECTION = "Scraped"
        # Document type of a course entry
        self.DOCUMENT_TYPE = "course"

    @staticmethod
    def get_soup(link):
        return BeautifulSoup((requests.get(link)).text, 'html.parser')

    def parse(self):
        # Retrieves department list from Cal Poly
        top_link = 'http://catalog.calpoly.edu/coursesaz/'
        top_soup = self.get_soup(top_link)

        departments_az = top_soup.find(id="/coursesaz/")
        department_urls = [department.get('href')
                           for department in departments_az.find_all('a')]

        # This will store all courses that will be added to firebase. These
        # will all be written at once with a "batch write" to avoid calling
        # firebase a high number of times
        firebase_transactions = []

        # Retrieves course info for each department
        for department in department_urls:
            # Extracts the department name from the URL
            dep_name = (department.rsplit('/', 2)[1]).upper()

            # Gets raw list of courses and info for department
            dep_link = 'http://catalog.calpoly.edu' + department
            dep_soup = self.get_soup(dep_link)
            courses = dep_soup.findAll("div", {"class": "courseblock"})

            # Extract info for each class and create dictonary object
            for course in courses:
                course_name_and_units = (course.find("p", {"class": "courseblocktitle"})).get_text()
                course_name, course_units = course_name_and_units.splitlines()
                course_units = course_units.split(' ',1)[0]

                course_terms_and_reqs = (course.find("div", {"class": "noindent courseextendedwrap"})).get_text()

                section = None
                course_prereqs, course_coreqs, course_conc, course_rec, course_terms = [],[],[],[],[]

                for word in course_terms_and_reqs.split():
                    if word.endswith(':'):
                        if word == 'Offered:':
                            section = 'terms'
                        # Last term (F,W,SP, etc) will be appended to the front of "Prerequisite:" or whatever category comes
                        # immediately after terms offered, so "str.endswith(blah)" has to be done instead of "str == blah"
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

                def join_or_na_if_none(words):
                    if words:
                        return ' '.join(words)
                    else:
                        return 'NA'

                course_prereqs = join_or_na_if_none(course_prereqs)
                course_coreqs = join_or_na_if_none(course_coreqs)
                course_conc = join_or_na_if_none(course_conc)
                course_rec = join_or_na_if_none(course_rec)
                course_terms = join_or_na_if_none(course_terms)

                # Define data in a python dictionary
                document = {
                    "department": dep_name,
                    "courseName": course_name,
                    "units": course_units,
                    "prerequisites": course_prereqs,
                    "corequisites": course_coreqs,
                    "concurrent": course_conc,
                    "recommended": course_rec,
                    "termsTypicallyOffered": course_terms
                }

                print("Storing course: {} with document {}".format(
                    course_name, document))

                # Create firebase Transaction type and add to list for
                # batched write
                firebase_transactions.append(Transaction(self.COLLECTION,
                                                         course_name,
                                                         document,
                                                         self.DOCUMENT_TYPE))

        # Call the firebase proxy interface to add course entries to
        # firestore
        self.firebase_proxy.batched_write(firebase_transactions)