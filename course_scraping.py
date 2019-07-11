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

            # Extract info for each class and populate spreadsheet
            for course in courses:
                course_name_and_units =\
                    (course.find("p", {"class": "courseblocktitle"})).get_text()
                course_name, course_units = course_name_and_units.splitlines()
                course_units = course_units.split(' ', 1)[0]

                course_terms_and_prereqs = (course.find(
                    "div", {"class": "noindent courseextendedwrap"})).get_text()
                try:
                    course_terms, course_prereqs =\
                        course_terms_and_prereqs.split("Prerequisite: ")
                except IndexError:
                    course_prereqs = "NA"
                    course_terms = course_terms_and_prereqs\
                        .split("Term Typically Offered: ", 1)[1]
                except ValueError:
                    # Yes this is the same behavior as an IndexError
                    course_prereqs = "NA"
                    course_terms = course_terms_and_prereqs\
                        .split("Term Typically Offered: ", 1)[1]
                else:
                    course_terms = course_terms\
                        .split("Term Typically Offered: ", 1)[1]

                # Define data in a python dictionary
                document = {
                    "department": dep_name,
                    "courseName": course_name,
                    "units": course_units,
                    "prerequisites": course_prereqs,
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
