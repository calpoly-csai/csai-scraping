import scraper

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

    @scraper.scraper
    def scrape(self, all_departments=False, no_upload=False):
        """
        Scrapes course information and requirements to Firebase

        args:
        all_departments (Bool): scrapes all departments if True, or just CPE
            and CSC if False (default False)
        no_upload (Bool): Used by scraper.py to control uploading vs just returning
            scraped data

        returns:
        firebase_transactions ([Transaction]) : A list of Transaction objects
            containing information for each course
        """
        # Retrieves department list from Cal Poly
        if all_departments:
            top_link = "http://catalog.calpoly.edu/coursesaz/"
            top_soup = scraper.get_soup(top_link, ver=False)
            # Changed scraping method because source for visible links changed, but
            # old links are still in the source and cause some 404 errors
            departments_az = top_soup.find('table')
            department_urls = [department.get('href')
                               for department in departments_az.find_all('a')
                               if department.get('href')]
        else:
            department_urls = ['/coursesaz/csc/', '/coursesaz/cpe/']

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
            dep_soup = scraper.get_soup(dep_link)
            courses = dep_soup.findAll("div", {"class": "courseblock"})

            # Extract info for each class and populate spreadsheet
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

                #print("Storing course: {} with document {}".format(
                #    course_name, document))

                # Create firebase Transaction type and add to list for
                # batched write
                firebase_transactions.append(Transaction(self.COLLECTION,
                                                         course_name,
                                                         document,
                                                         self.DOCUMENT_TYPE))

        # Call the firebase proxy interface to add course entries to
        # firestore
        return firebase_transactions


if __name__ == '__main__':
    courses = CourseScraper(scraper.blank_proxy).scrape(no_upload=True)
    for c in courses:
        print(c.document_name)
        for key, value in c.document.items():
            print(f'\t{key}: {value}')
        print()
