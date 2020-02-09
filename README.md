# Nimbus scraping
A collection of utilities for scraping data for Cal Poly's Nimbus voice assistant.

## Installation
Install [pipenv](https://pipenv.readthedocs.io/en/latest/) with [pip](https://pip.pypa.io/en/stable/) and run
```bash
pipenv install
```
in the project folder.

## Usage
```python
import sustainer

# returns a JSON string of CSV data from all modules
json = sustainer.scrape_all()
```

```python
# For any module "scraping_module",
from scraping_module import ScrapingModule

s = ScrapingModule()

# returns a CSV string of scraped data
csv = s.scrape()
```

## Supported Data
#### schedules_scraper.py
* Professor contact information (office, phone, email)
* Class section times (start / end)
* Which professor is teaching which class
* Class locations
* Class types (lab / lec)

#### club_scraper.py
* Contact information (phone, email, box, contact person)
* Advisor info (name, phone, email)
* Affiliations and types
* Descriptions

#### course_scraper.py
* Course requirements (coreq, prereq, concurrent, and recommended)
* Units
* Department
* Terms typically offered

#### calendar_scraper.py
* Academic calendar events and dates

#### faculty_scraper.py
* Faculty contact information (office, phone, email)
* Professor research interests

## Architecture
![Nimbus Scraping Architecture](https://i.imgur.com/ongMSm6.png)

## TODO

- [ ] Integrate scrapers into Nimbus API
- [ ] Add reporting when website format changes are detected
- [ ] Add GE areas to course_scraper
- [ ] Create degree program scraper ([catalog.calpoly.edu/programsaz/](http://catalog.calpoly.edu/programsaz/))
- [ ] Integrate more calendars into calendar_scraper

## Contributing
Feel free to make pull requests or report issues. For major changes, please open an issue first to discuss. Also, check out onboarding.txt (coming soon)


## License
[MIT](https://choosealicense.com/licenses/mit/)
