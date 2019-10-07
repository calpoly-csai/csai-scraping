import scraper
from time import sleep

from firebase.firebase_proxy import FirebaseProxy
from transaction import Transaction


class CurriculumScraper:
    def __init__(self, firebase_proxy: FirebaseProxy):
        self.firebase_proxy = firebase_proxy

        self.COLLECTION = "Scraped"
        self.DOCUMENT_TYPE = "curriculum"
        self.REST_TIME = 100  # Time between requests in ms

    def parse_single_curriculum(self, url):
        """ Scrapes data from a single curriculum page """

        soup = scraper.get_soup(url, ver=False)
        tables = soup.find_all("table")
        ge_curriculum_table = tables[2]
        for row in ge_curriculum_table.find_all('tr'):
            cols = row.find_all('td')
            print(cols)

        # # Information is stored in different blocks for staff and faculty
        # if url.rsplit("/", 3)[1] == "staff":
        #     main_info_text = [l.text for l in soup.find_all("span")]
        #     table = soup.find("table")
        # else:
        #     faculty_main_info = soup.find(id="facultyMainBlock")
        #     table = faculty_main_info.find("table")
        #     main_info_text = faculty_main_info.text.splitlines()

        #     # Getting the research interests for every professor
        #     # Doesn't work for Hasmik Gharibyan and other people who have a biography
        #     faculty_additional_info = soup.find(class_="facultyBlock")
        #     if faculty_additional_info is not None and faculty_additional_info.span:
        #         research_interests = []
        #         for string in faculty_additional_info.stripped_strings:
        #             research_interests.append(string)

        # found_office = found_phone = found_email = False

        # for line in main_info_text:
        #     if not found_office:
        #         if line.startswith("Office:"):
        #             office = line.rsplit(" ", 1)[1]
        #             found_office = True
        #     if not found_phone:
        #         if line.startswith("Phone "):
        #             phone = line.rsplit(" ", 1)[1]
        #             found_phone = True
        #     if not found_email:
        #         if line.startswith("Email:"):
        #             # For faculty pages, the character following "Email:" is not a space but \xa0
        #             try:
        #                 first_split = line.split("\xa0", 1)[1]
        #             except IndexError:
        #                 first_split = line.split(" ", 1)[1]
        #             email = first_split.split("(", 1)[0] + "@calpoly.edu"
        #     if found_office and found_phone and found_email:
        #         break

        # office_hours = dict()

        # # TODO: Add single-line office hour parsing.
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

        curriculum_info = {
            "ge_curriculum": ge_curriculum
        }

        # return Transaction(
        #     self.COLLECTION,
        #     major,
        #     curriculum_info,
        #     self.DOCUMENT_TYPE,
        # )

    @scraper.scraper
    def scrape(self, no_upload=False):
        """
        Scrapes data from the CPE page

        args:
        no_upload (Bool): Used by scraper.py to control uploading vs just returning
            scraped data

        returns:
        firebase_transactions ([Transaction]): A list of Transactions with
            data for each employee
        """

        firebase_transactions = []

        # CPE employees
        # cpe_top_link = "http://catalog.calpoly.edu/collegesandprograms/collegeofengineering/computerengineering/bscomputerengineering/"
        # cpe_top = scraper.get_soup(cpe_top_link)
        info = self.parse_single_curriculum(
            "http://catalog.calpoly.edu/collegesandprograms/collegeofengineering/computerengineering/bscomputerengineering/")
        # firebase_transactions.append(info)
        # sleep(self.REST_TIME / 1000)
        # for link in cpe_top.find_all("a", href=True):
        #     nav = link["href"]
        #     if (nav.startswith("/faculty/") or nav.startswith("/staff")) and (
        #         nav != "/faculty/" and nav != "/staff/"
        #     ):
        #         info = self.parse_single_curriculum("https://cpe.calpoly.edu" + nav)
        #         firebase_transactions.append(info)
        #         sleep(self.REST_TIME / 1000)

        # # CSC employees
        # csc_top_link = "https://csc.calpoly.edu/faculty/"
        # # Verification turned off; read main note in self.parse_single_employee
        # csc_top = scraper.get_soup(csc_top_link, ver=False)
        # for link in csc_top.find_all("a", href=True):
        #     nav = link["href"]
        #     if (nav.startswith("/faculty/") or nav.startswith("/staff")) and (
        #         nav != "/faculty/" and nav != "/staff/"
        #     ):
        #         info = self.parse_single_employee("https://csc.calpoly.edu" + nav)
        #         firebase_transactions.append(info)
        #         sleep(self.REST_TIME / 1000)

        return firebase_transactions


if __name__ == "__main__":
    faculty = CurriculumScraper(scraper.blank_proxy).scrape(no_upload=True)
    print("Done")
    # for f in faculty:
    #     print(f.document_name)
    #     for key, value in f.document.items():
    #         if key == "office_hours":
    #             print("\toffice_hours:")
    #             if value == "NA":
    #                 print("\t\tNA")
    #             else:
    #                 for key2, value2 in value.items():
    #                     print(f"\t\t{key2}")
    #                     for key3, value3 in value2.items():
    #                         print(f"\t\t\t{key3}: {value3}")
    #         else:
    #             print(f"\t{key}: {value}")
    #     print()
