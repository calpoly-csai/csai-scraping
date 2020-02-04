from bs4 import BeautifulSoup
from bs4.dammit import EncodingDetector
import urllib3
import requests
import re
import pandas as pd
from tabulate import tabulate


def get_graduate_programs(url):
    """Gets links to all available graduate degrees at Cal Poly"""

    html_page = requests.get(url)
    soup = BeautifulSoup(html_page.text, "html.parser")

    # Graduate program names and links are found within a single div class
    graduate_program_links_list = soup.find('div', {'id': 'graduatetextcontainer'})

    # Add each graduate program name and link into a dictionary
    # For every graduate program, go into the respective link and scrape
    graduate_programs = {}
    for a in graduate_program_links_list.find_all('a', href=True):
        if a.parent.parent == graduate_program_links_list:
            graduate_programs.setdefault(a.string, [])
            graduate_programs[a.string].append(scrape_program_courses("http://catalog.calpoly.edu" + a.get('href')))
            # graduate_programs[a.string].append(a.get('href'))

        # Call a function to get general information on each graduate program
        # Most links to graduate programs have a bio, and some do not
        # get_general_information(a.get('href'))

    del graduate_programs['Masters Degrees']
    del graduate_programs['Graduate Certificates']
    del graduate_programs['Back to Top']

    return pd.DataFrame(graduate_programs).to_csv(None, index=False)

def scrape_program_courses(url):
    """Gets the course information specific to each program. E.g. required courses,
    general education courses, course units, etc."""

    # Try except block for finding tables on the page...
    try:

        html_page = requests.get(url)
        soup = BeautifulSoup(html_page.content, 'lxml')
        table = soup.find_all('table')
        dataframe = pd.read_html(str(table))
        return tabulate(dataframe[0], headers='keys', tablefmt='psql')
    except:
        return "No table on this page"




def get_general_information(url):
    """This function is a helper function to get the graduate program general information"""
    pass


if __name__ == "__main__":
    pass
    dict =  get_graduate_programs("http://catalog.calpoly.edu/programsaz/#graduatetext")
    print(dict)
    # for i in dict:
    #     print(i + "\n", "\n".join(dict[i]))
