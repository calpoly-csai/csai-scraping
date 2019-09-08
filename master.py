# TODO: Add logging and version control of scraped data

# MODULES
from firebase.firebase_proxy import FirebaseProxy
from calendar_scraper import CalendarScraper
from course_scraper import CourseScraper
from faculty_scraper import FacultyScraper
from club_scraper import ClubScraper

if __name__ == "__main__":
    firebase_proxy = FirebaseProxy() # Add firebase proxy here

    modules = [CalendarScraper(firebase_proxy),
               CourseScraper(firebase_proxy),
               FacultyScraper(firebase_proxy),
               ClubScraper(firebase_proxy)]

    for s in modules:
        s.scrape()
