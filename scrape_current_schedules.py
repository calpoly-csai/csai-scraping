import schedules_scraper as ss
import os

if __name__=='__main__':
    url = 'https://schedules.calpoly.edu/depts_52-CENG_curr.htm'
    dfs = ss.scrape_schedules_from_url(url, preprocess=ss.preprocess_schedules)

    if not os.path.exists('csv'):
        os.mkdir('csv')

    for df in dfs:
        title = df['Department'][0]
        title.replace('-','_')
        title.replace(' ','_')
        df.to_csv(f'csv/{title}.csv')