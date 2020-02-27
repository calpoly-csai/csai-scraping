"""
Title: Faculty Scraper Class
Author: Cameron Toy
Date: 2/3/2020
Organization: Cal Poly CSAI
Description: Downloads Cal Poly map data in .kmz format and converts it to CSV
"""
import json

import requests
from zipfile import ZipFile
from io import BytesIO
import xml.sax.handler
from barometer import barometer, SUCCESS, ALERT, INFO, DEBUG, ERR


class LocationScraper:

    def __init__(self):
        self.LOCATIONS_API = 'http://0.0.0.0:8080/new_data/locations'
        self.TOP_LINK = 'https://afd.calpoly.edu/facilities/campus-maps/docs/Cal_Poly_Buildings.kmz'

    @staticmethod
    def transform_location_to_db(location: str):
        loc_split = location.split(',')
        db_location = {
            'building_number': loc_split[0],
            'name': loc_split[1],
            'longitude': loc_split[2],
            'latitude': loc_split[3],
        }

        return db_location

    @barometer
    def scrape(self):
        """
        Downloads and parses a .kmz file from Cal Poly containing location data

        returns:
            str: A CSV string of parsed data
        """
        print(DEBUG, f"Starting location data scrape: TOP_LINK={self.TOP_LINK}")
        try:
            page = requests.get(self.TOP_LINK)
        except requests.exceptions.RequestException as e:
            print(ALERT, e)
            return None
        print(SUCCESS, f"Retrieved location data from {self.TOP_LINK}")

        # I don't know the ways the rest of this can fail, so no useful log messages here

        # Extract contents of .kmz file
        archive = ZipFile(BytesIO(page.content), 'r')

        try:
            kml = archive.open('doc.kml', 'r')
        except KeyError as e:
            print(ERR, f"Item not found: {e}")
        else:
            print(SUCCESS, "Found doc.kml")

        # .kmz files holds a .kml file that just contains styled XML
        try:
            parser = xml.sax.make_parser()
        except Exception as e:
            print(ERR, f"Failed to create parser: {e}")
        else:
            print(SUCCESS, "Created parser")
        try:
            handler = PlacemarkHandler()
        except Exception as e:
            print(ERR, f"Failed to create handler: {e}")
        else:
            print(SUCCESS, "Created handler")

        parser.setContentHandler(handler)

        try:
            parser.parse(kml)
        except Exception as e:
            print(ERR, f"Failed to parse .kml file: {e}")
        archive.close()

        output = self.build_table(handler.mapping)

        locations_request = json.dumps({
            'locations': [self.transform_location_to_db(location)
                          for location in output.split('\n')[1:-1]]
        })
        requests.post(url=self.LOCATIONS_API,
                      json=locations_request)

        return output

    @staticmethod
    def build_table(mapping):
        """
        Creates a CSV string from a dict containing .kmz data

        args:
            mapping (dict(str:str)): A dict whose keys are building names and keys are coordinates

        returns:
            str: A CSV string of parsed data
        """
        sep = ','

        output = f'BUILDING_NUMBER{sep}NAME{sep}LONGITUDE{sep}LATITUDE\n'
        points = ''
        lines = ''
        shapes = ''
        for key in mapping:

            # Separates building numbers and names
            try:
                building_number, name = key.split(' ', 1)
            except ValueError:
                building_number = key
                name = 'NA'
            coord_str = mapping[key]['coordinates'] + sep

            # Removes unused height coordinate
            coord_str = coord_str[0:-1].rsplit(',',1)[0]

            stem = f'{building_number}{sep}{name}{sep}{coord_str}\n'
            if 'LookAt' in mapping[key]: #points
                points += stem
            elif 'LineString' in mapping[key]: #lines
                lines += stem
            else: #shapes
                shapes += stem
        output += f'{points}{lines}{shapes}'

        print(SUCCESS, f"Done! Scraped {len(output.splitlines())} locations")
        return output


class PlacemarkHandler(xml.sax.handler.ContentHandler):
    """
    Simple API for XML (SAX) handler for parsing the XML contained in .kml files
    """

    def __init__(self):
        self.inName = False
        self.inPlacemark = False
        self.mapping = {}
        self.buffer = ""
        self.name_tag = ""

    def startElement(self, name, attributes):
        """
        Called at starting elements (<Placemark>, <name>, etc)

        args:
            name (str): Element name to be parsed
        """
        if name == "Placemark": # on start Placemark tag
            self.inPlacemark = True
            self.buffer = ""
        if self.inPlacemark:
            if name == "name": # on start title tag
                self.inName = True # save name text to follow

    def characters(self, data):
        """
        Adds text between starting and ending elements to buffer

        args:
            data (str): Text between elements
        """
        if self.inPlacemark: # on text within tag
            self.buffer += data # save text if in title

    def endElement(self, name):
        """
        Called at ending elements (</Placemark>, <name>, etc)

        args:
            name (str): Element name to be parsed
        """
        self.buffer = self.buffer.strip('\n\t')

        if name == "Placemark":
            self.inPlacemark = False
            self.name_tag = "" #clear current name

        elif name == "name" and self.inPlacemark:
            self.inName = False # on end title tag
            self.name_tag = self.buffer.strip()
            self.mapping[self.name_tag] = {}
        elif self.inPlacemark:
            if name in self.mapping[self.name_tag]:
                self.mapping[self.name_tag][name] += self.buffer
            else:
                self.mapping[self.name_tag][name] = self.buffer
        self.buffer = ""

LocationScraper().scrape(verbosity=8)