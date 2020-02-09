"""
Title: Club Scraper Class
Author: Cameron Toy
Date: 1/22/2020
Organization: Cal Poly CSAI
Description: Scrapes club data from the Cal Poly website
"""

import scraper_base
import requests
import pandas as pd
from barometer import barometer, SUCCESS, ALERT, INFO, DEBUG


class ClubScraper:

    def __init__(self):
        self.TOP_LINK = 'https://www.asi.calpoly.edu/club_directories/listing_bs/'
        # Doesn't contain 'Contact Email' because that name is used for two different fields.
        # Workaround in scrape method.
        self.INFO_ENTRY_PAIRS = {
            'Contact Person:': 'CONTACT_PERSON',
            'Contact Phone:': 'CONTACT_PHONE',
            'Advisor:': 'ADVISOR',
            'Advisor Phone:': 'ADVISOR_PHONE',
            'Advisor Email:': 'ADVISOR_EMAIL',
            'Box:': 'BOX',
            'Affiliation:': 'AFFILIATION',
            'Type(s):': 'TYPES',
            'Description:': 'DESCRIPTION'
        }

    @barometer
    def scrape(self):
        """
        Scrapes club information to CSV

        returns:
            str: A CSV string of scraped data
        """
        print(INFO, f'Starting scrape on {self.TOP_LINK}')
        try:
            top = scraper_base.get_soup(self.TOP_LINK)
        except requests.exceptions.RequestException as e:
            print(ALERT, e)
            return None
        print(SUCCESS, f'Retrieved club list')
        raw = [l.text.strip() for l in top.find_all('span')]
        # Filters out some info we don't need
        info = [x for x in raw if x and x != "Website" and x != "Homepage:"]
        info.pop(0)  # Don't need first line

        current_club = None
        info_len = len(info)
        club_info = dict()
        scraped_clubs = []
        i = 0

        while i < info_len:
            line = info[i]
            if line in self.INFO_ENTRY_PAIRS:
                next_line = info[i+1]
                entry_name = self.INFO_ENTRY_PAIRS[line]
                if next_line.endswith(':'):
                    club_info[entry_name] = 'NA'
                    i += 1
                else:
                    club_info[entry_name] = next_line
                    i += 2
            elif line == "Contact Email:":
                next_line = info[i+1]
                try:
                    bool(club_info['CONTACT_EMAIL'])  # Checks if there's already a contact_email entry.
                except KeyError:
                    if next_line.endswith(':'):
                        club_info['CONTACT_EMAIL'] = 'NA'
                        i += 1
                    else:
                        club_info['CONTACT_EMAIL'] = next_line
                        i += 2
                else:
                    # Two fields are called "Contact Email"--the email of the main contact for the club, and the club's
                    # official email to contact them. For now, the official email is called "contact_email_2"
                    if '@' in next_line:  # Next line could be the name of another club; doesn't end in ':'
                        club_info['CONTACT_EMAIL_2'] = next_line
                        i += 2
                    else:
                        club_info['CONTACT_EMAIL_2'] = 'NA'
                        i += 1
            else:
                # Checking len(club_info) filters unused addresses and stuff that get parsed as club names.
                if current_club and len(club_info) != 0:
                    club_info['NAME'] = current_club
                    scraped_clubs.append(club_info)
                    print(DEBUG, f'Scraped {current_club}')
                else:
                    print(DEBUG, f'Discarding non-club {current_club}')
                club_info = dict()
                current_club = line
                i += 1

        print(SUCCESS, f'Done! Scraped {len(scraped_clubs)} clubs')
        return pd.DataFrame(scraped_clubs).to_csv(None, index=False)
