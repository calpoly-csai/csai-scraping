# Scrapes and logs course information for Cal Poly
# Made by Cameron Toy for Cal Poly Computer Science and Artificial Intelligence

import requests
from bs4 import BeautifulSoup
import openpyxl
from time import sleep

def get_soup(link):
    return BeautifulSoup((requests.get(link)).text, 'html.parser')

# Retrieves department list from Cal Poly
print('Retrieving Cal Poly department names...\n')
top_link = 'http://catalog.calpoly.edu/coursesaz/'
top_soup = get_soup(top_link)

departments_az = top_soup.find(id="/coursesaz/")
department_urls = [department.get('href') for department in departments_az.find_all('a')]

# Retrieves course info for each department
for department in department_urls:
    sleep(1)
    # Extracts the department name from the URL
    dep_name = (department.rsplit('/',2)[1]).upper()
    print("Scraping " + dep_name + " department...\n")
    # Creates a new spreadsheet
    wb = openpyxl.Workbook()
    main = wb.active
    main.title = dep_name
    main["A1"] = 'Course name'
    main["B1"] = 'Units'
    main["C1"] = 'Prerequisites'
    main["D1"] = "Corequisites"
    main["E1"] = "Concurrent"
    main["F1"] = 'Recommended'
    main["G1"] = 'Terms Typically Offered'
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

        row_string = str(row)
        main["A" + row_string] = course_name
        main["B" + row_string] = course_units
        main["C" + row_string] = course_prereqs
        main["D" + row_string] = course_coreqs
        main["E" + row_string] = course_conc
        main["F" + row_string] = course_rec
        main["G" + row_string] = course_terms
        row += 1

    wb.save(dep_name + ".xlsx")

print('\n\nALL DONE')
