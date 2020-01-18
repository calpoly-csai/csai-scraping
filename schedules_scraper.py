import pandas as pd
from bs4 import BeautifulSoup
import requests


# get_soup : str -> BeautifulSoup
def get_soup(url, ver=True):
    """Simplifies pulling a website into a BeautifulSoup object"""
    page = requests.get(url, verify=ver)
    # lxml used for speed
    return BeautifulSoup(page.text, 'lxml')


# separate_dfs : DataFrame -> list(DataFrame)
def separate_dfs(df, add_name=False):
    """
    Separates DataFrame into multiple DataFrames. As a quirk of how Pandas parses HTML,
    if a df has a MultiIndex, it's almost always because that HTML table is made up of
    multiple sub tables. This method of splitting dfs assumes there's one "actual"
    heading row and the other is the sub-table identifier.
    Also removes MultiIndex.

    Args:
        df: DataFrame to split
        add_name: If True, adds a ".name" attribute to each sub-table based on the
            identifying header.

    Returns:
        A list of sub-tables (or the original table if there are none)
    """

    # name_df : DataFrame -> str -> None
    def name_df(d, s):
        if add_name:
            d.name = s

    # Finds indicies of rows where all values are equal
    indicies = list(df[df.eq(df.iloc[:, 0], axis=0).all(1)].index)

    # If there's no separation or MultiIndex, return original df
    if len(indicies) == 0 or type(df.columns) != pd.core.indexes.multi.MultiIndex:
        return [df]
    else:
        # Find which header is all the same value (sub-table identifying header)
        header_one = [a for a,b in df.columns]
        header_two = [b for a,b in df.columns]
        if len(set(header_one)) == 1:
            if len(set(header_two)) == 1:
                raise ValueError('MultiIndex with no multi-valued headers')
            else:
                df_name = header_one[0]
                df.columns = header_two
        elif len(set(header_two)) == 1:
            df_name = header_two[0]
            df.columns = header_one
        else:
            raise ValueError('MultiIndex with multiple multi-valued headers')

        prev_index = -1
        dfs = []
        for i in indicies + [len(df)]:
            sub_df = df.iloc[prev_index+1:i,:].reset_index(drop=True)
            name_df(sub_df, df_name)
            df_name = df.iloc[i%len(df),:][0]
            dfs.append(sub_df)
            prev_index = i

    return dfs


# preprocess_schedules : DataFrame -> DataFrame
def preprocess_schedules(df):
    """
    Combines Course and Sect col.s, adds Department col.

    Args:
        df: One DataFrame from split schedules data

    Returns:
        A processed DataFrame
    """
    # Remove extraneous "Unnamed*" columns introduced by Pandas
    df.dropna(axis='columns', how='all', inplace=True)
    # If first row is the same as the header, drop it
    if all(df.iloc[0,:] == df.columns):
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

    return df


# scrape_schedules_from_html : str -> f(DataFrame -> DataFrame) -> list(DataFrame)
def scrape_schedules_from_html(html, preprocess=None):
    """
    Scrapes schedule from HTML string

    Args:
        html: HTML string of website
        preprocess: A function of type DataFrame -> DataFrame that
            will be applied to each parsed DataFrame before scraping

    Returns:
        A list of scraped DataFrames
    """
    dfs = pd.read_html(html)
    separated = []
    for df in dfs:
        separated.extend(separate_dfs(df, add_name=True))
    if preprocess is not None:
        separated = [preprocess(d) for d in separated]

    return separated


# scrape_schedules_from_url : str -> bool -> f(DataFrame -> DataFrame) -> list(DataFrame)
def scrape_schedules_from_url(url, verify=True, preprocess=None):
    soup = get_soup(url, verify)
    return scrape_schedules_from_html(str(soup), preprocess)


# scrape_schedules_from_file : str -> bool -> f(DataFrame -> DataFrame) -> list(DataFrame)
def scrape_schedules_from_file(path, preprocess=None):
    with open(path, 'r') as f:
        text = f.read()
    return scrape_schedules_from_html(text, preprocess)

