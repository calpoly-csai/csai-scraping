# Scrapes and logs course information for Cal Poly
# Made by Cameron Toy for Cal Poly Computer Science and Artificial Intelligence

import requests
from bs4 import BeautifulSoup
import openpyxl
from time import sleep

def get_soup(link):
    return BeautifulSoup((requests.get(link)).text, 'html.parser')

# Retrieves department list from Cal Poly
top_link = 'http://catalog.calpoly.edu/coursesaz/'
top_soup = get_soup(top_link)

departments_az = top_soup.find(id="/coursesaz/")
department_urls = [department.get('href') for department in departments_az.find_all('a')]

# Retrieves course info for each department
for department in department_urls:
    sleep(1)
    # Extracts the department name from the URL
    dep_name = (department.rsplit('/',2)[1]).upper()

    # Creates a new spreadsheet
    wb = openpyxl.Workbook()
    main = wb.active
    main.title = dep_name
    main["A1"] = 'Course name'
    main["B1"] = 'Units'
    main["C1"] = 'Prerequisites'
    main["D1"] = 'Terms Typically Offered'
    row = 2

    # Gets raw list of courses and info for department
    dep_link = 'http://catalog.calpoly.edu' + department
    dep_soup = get_soup(dep_link)
    courses = dep_soup.findAll("div", {"class": "courseblock"})

    # Extract info for each class and populate spreadsheet
    for course in courses:
        course_name_and_units = (course.find("p", {"class": "courseblocktitle"})).get_text()
        course_name, course_units = course_name_and_units.splitlines()
        course_units = course_units.split(' ',1)[0]

        course_terms_and_prereqs = (course.find("div", {"class": "noindent courseextendedwrap"})).get_text()
        try:
            course_terms, course_prereqs = course_terms_and_prereqs.split("Prerequisite: ")
        except IndexError:
            course_prereqs = "NA"
            course_terms = course_terms_and_prereqs.split("Term Typically Offered: ",1)[1]
        except ValueError:
            # Yes this is the same behavior as an IndexError
            course_prereqs = "NA"
            course_terms = course_terms_and_prereqs.split("Term Typically Offered: ",1)[1]
        else:
            course_terms = course_terms.split("Term Typically Offered: ",1)[1]

        row_string = str(row)
        main["A" + row_string] = course_name
        main["B" + row_string] = course_units
        main["C" + row_string] = course_prereqs
        main["D" + row_string] = course_terms
        row += 1

    wb.save(dep_name + ".xlsx")
