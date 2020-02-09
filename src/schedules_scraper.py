"""
Title: Schedules Scraper Class
Author: Cameron Toy
Date: 1/22/2020
Organization: Cal Poly CSAI
Description: Scrapes class and professor data from the Cal Poly schedules site
"""

import pandas as pd
import scraper_base
import requests
from barometer import barometer, SUCCESS, ALERT, INFO, DEBUG

class SchedulesScraper:

    def __init__(self):
        self.TOP_LINK = 'https://schedules.calpoly.edu/depts_52-CENG_curr.htm'

    def separate_dfs(self, df, add_name=False):
        """
        Separates DataFrame into multiple DataFrames. As a quirk of how Pandas parses HTML,
        if a df has a MultiIndex, it's almost always because that HTML table is made up of
        multiple sub tables. This method of splitting dfs assumes there's one "actual"
        heading row and the other is the sub-table identifier.
        Also removes MultiIndex.

        args:
            df: DataFrame to split
            add_name: If True, adds a ".name" attribute to each sub-table based on the
                identifying header.

        returns:
            A list of sub-tables (or the original table if there are none)
        """
        print(DEBUG, f"Calling separate_dfs: add_name={add_name}")

        # name_df : DataFrame -> str -> None
        def name_df(d, s):
            if add_name:
                d.name = s

        # Finds indicies of rows where all values are equal
        indicies = list(df[df.eq(df.iloc[:, 0], axis=0).all(1)].index)

        # If there's no separation or MultiIndex, return original df
        if len(indicies) == 0 or type(df.columns) != pd.core.indexes.multi.MultiIndex:
            print(DEBUG, f"No sub-dfs. Returning original.")
            return [df]
        else:
            # Find which header is all the same value (sub-table identifying header)
            header_one = [a for a,b in df.columns]
            header_two = [b for a,b in df.columns]
            if len(set(header_one)) == 1:
                if len(set(header_two)) == 1:
                    print(ERR, "MultiIndex with no multi-valued headers")
                    raise ValueError('MultiIndex with no multi-valued headers')
                else:
                    df_name = header_one[0]
                    df.columns = header_two
            elif len(set(header_two)) == 1:
                df_name = header_two[0]
                df.columns = header_one
            else:
                print(ERR, "MultiIndex with multiple multi-valued headers")
                raise ValueError('MultiIndex with multiple multi-valued headers')
            print(DEBUG, "Found sub-table identifying header")

            prev_index = -1
            dfs = []
            num_processed_dfs = 0
            for i in indicies + [len(df)]:
                num_processed_dfs += 1
                sub_df = df.iloc[prev_index+1:i,:].reset_index(drop=True)
                name_df(sub_df, df_name)
                df_name = df.iloc[i%len(df),:][0]
                print(DEBUG, f"Found sub-df {df_name} from indicies {prev_index + 1} to {i}")
                dfs.append(sub_df)
                prev_index = i

        print(DEBUG, f"Separated df into {len(dfs)} sub-dfs")
        return dfs


    def preprocess_schedules(self, df):
        """
        Combines Course and Sect col.s, adds Department col.

        args:
            df: One DataFrame from split schedules data

        returns:
            A processed DataFrame
        """
        print(DEBUG, f"Calling preprocess_schedules: df={df.name}")
        # Remove extraneous "Unnamed*" columns introduced by Pandas
        df.dropna(axis='columns', how='all', inplace=True)
        # If first row is the same as the header, drop it
        if all(df.iloc[0,:] == df.columns):
            print(DEBUG, "First row is the same as the header. Dropping it.")
            df.drop(0, inplace=True)
            df.reset_index(drop=True, inplace=True)

        # Combine 'Course' and 'Sect" columns as 'Course'
        for i in range(len(df)):
            c = df['Course'][i]
            s = df['Sect'][i]
            if pd.isna(c) or pd.isna(s):
                continue
            else:
                df['Course'][i] = f'{c}_{s}'

        df['Department'] = [df.name] * len(df)

        # Drop 'Sect' column
        df.drop('Sect', axis='columns', inplace=True)

        if 'Office Hours' in df:
            print(DEBUG, "Found office hours column. Dropping it.")
            df.drop('Office Hours', axis='columns', inplace=True)

        # Make column headings uppercase
        df.columns = [s.upper() for s in df.columns]

        return df

    def scrape_schedules_from_html(self, html, preprocess=None):
        """
        Scrapes schedule from HTML string

        args:
            html: HTML string of website
            preprocess: A function of type DataFrame -> DataFrame that
                will be applied to each parsed DataFrame before scraping

        returns:
            A list of scraped DataFrames
        """
        print(DEBUG, f"Calling scrape_schedules_from_html: preprocess={preprocess}")
        dfs = pd.read_html(html)
        if not dfs:
            print(ALERT, "Didn't find any tables on page. Aborting scrape.")
            return None
        print(INFO, f"Found {len(dfs)} table(s)")
        separated = []
        for df in dfs:
            separated.extend(self.separate_dfs(df, add_name=True))
        print(INFO, f"Split {len(dfs)} df(s) into {len(separated)} sub-df(s)")
        if preprocess is not None:
            separated = [preprocess(d) for d in separated]
        return separated

    def scrape_schedules_from_url(self, url, verify=True, preprocess=None):
        try:
            soup = scraper_base.get_soup(url, verify)
        except requests.exceptions.RequestException as e:
            print(ALERT, e)
            return None
        print(SUCCESS, "Retrieved schedules page")
        return self.scrape_schedules_from_html(str(soup), preprocess)

    def scrape_schedules_from_file(self, path, preprocess=None):
        with open(path, 'r') as f:
            text = f.read()
        return self.scrape_schedules_from_html(text, preprocess)

    @barometer
    def scrape(self):
        """
        Scrapes data from schedules.calpoly.edu to CSV

        returns:
            A CSV string of scraped data
        """
        print(INFO, f"Starting scrape on {self.TOP_LINK}")
        dfs = self.scrape_schedules_from_url(self.TOP_LINK, preprocess=self.preprocess_schedules)
        all_em = pd.concat(dfs)
        print(SUCCESS, f"Done! Scraped {len(all_em)} sections")
        csv_str = all_em.to_csv(None)
        return csv_str

