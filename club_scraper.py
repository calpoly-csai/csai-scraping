import scraper
from firebase.firebase_proxy import FirebaseProxy
from transaction import Transaction


class ClubScraper:

    def __init__(self, firebase_proxy: FirebaseProxy):
        self.firebase_proxy = firebase_proxy

        self.COLLECTION = 'Scraped'
        self.DOCUMENT_TYPE = 'club'
        self.TOP_LINK = 'https://www.asi.calpoly.edu/club_directories/listing_bs/'

    @scraper.scraper
    def scrape(self, no_upload=False):
        """
        Scrapes club information to Firebase

        args:
        no_upload (Bool): Used by scraper.py to control uploading vs just returning
            scraped data

        returns:
        firebase_transactions ([Transaction]): A list of Transactions with
            data for each club
        """
        top = scraper.get_soup(self.TOP_LINK)
        raw = [l.text.strip()
               for l in top.find_all('span')]
        info = [x for x in raw
                if x and x != "Website" and x != "Homepage:"]  # Filters out some crap
        info.pop(0)  # Don't need first line

        # Doesn't contain 'Contact Email' because that name is used for two different fields. Workaround below.
        info_entry_pairs = {
            'Contact Person:': 'contact_person',
            'Contact Phone:': 'contact_phone',
            'Advisor:': 'advisor',
            'Advisor Phone:': 'advisor_phone',
            'Advisor Email:': 'advisor_email',
            'Box:': 'box',
            'Affiliation:': 'affiliation',
            'Type(s):': 'types',
            'Description:': 'description'
        }

        current_club = None
        info_len = len(info)  # Prevents len() being called thousands of times during the main while loop
        club_info = dict()
        firebase_transactions = []
        i = 0

        while i < info_len:
            line = info[i]
            if line in info_entry_pairs:
                next_line = info[i+1]
                entry_name = info_entry_pairs[line]
                if next_line.endswith(':'):
                    club_info[entry_name] = 'NA'
                    i += 1
                else:
                    club_info[entry_name] = next_line
                    i += 2
            elif line == "Contact Email:":
                next_line = info[i+1]
                try:
                    bool(club_info['contact_email'])  # Checks if there's already a contact_email entry.
                except KeyError:
                    if next_line.endswith(':'):
                        club_info['contact_email'] = 'NA'
                        i += 1
                    else:
                        club_info['contact_email'] = next_line
                        i += 2
                else:
                    # Two fields are called "Contact Email"--the email of the main contact for the club, and the club's
                    # official email to contact them. For now, the official email is called "contact_email_2"
                    if '@' in next_line:  # Next line could be the name of another club; doesn't end in ':'
                        club_info['contact_email_2'] = next_line
                        i += 2
                    else:
                        club_info['contact_email_2'] = 'NA'
                        i += 1
            else:
                # Checking len(club_info) filters unused addresses and stuff that get parsed as club names.
                if current_club and len(club_info) != 0:
                    firebase_transactions.append(Transaction(self.COLLECTION,
                                                             current_club,
                                                             club_info,
                                                             self.DOCUMENT_TYPE))
                club_info = dict()
                current_club = line
                i += 1

        return firebase_transactions
