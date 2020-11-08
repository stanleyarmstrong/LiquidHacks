# Mouse Ranker Scrapers

MouseRank uses two main tools to populate our database of mice: product page scrapers and the MediaWiki API parse request scraper.

## Setup

### Install dependencies

We used pipenv for package control to make it easy to run our code regardless of platform.
Execute the platform-specific commands from the scraping directory.

Python 3 required

```shell script
cd ./scraping
python3 -m pip install pipenv
python3 -m pipenv install
```

## Usage

### Run the full scripts

Note: the environment variables `MONGO_USER` and `MONGO_PASS` must be set to your mongodb username and password for the script to run.

#### MediaWiki popularity scraper

```shell script
python -m pipenv run ./mediawiki_mouse_popularity_updater.py
```

#### Mouse product page scraper

```shell script
python -m pipenv run ./mouse_specs_scraper.py
```

## How it's programmed

### MediaWiki popularity scraper

1. List the http GET requests for each of the 'List of player mouse settings' pages on Liquipedia
2. Hash each request as a hex value, and check the `./cache` directory to see if the page has already been requested. This multiple requests of the same page.
3. Call the MediaWiki Parse API for each request, and save the html contents of the response to the cache with the hash value of the request as the file name
4. Scrape the newly-created html files using scrapy
    1. Collect the name of each mouse
    2. Count the number of esports players that use the mouse
    3. List the players that use the mouse
    4. Save the results to a json file
5. Since the json file will have duplicates, read all the entries and combine the counts of matching entries
6. Upload each mouse popularity count to MongoDB

### Mouse product page scrapers

1. Scrape a gaming mouse product list page for each manufacturer
2. Get a link to the product page for each individual mouse and scrape that page
3. Parse the information on the product page and save it to a json file
    1. Name
    2. Physical properties (Length, width, depth, weight, cable length, handedness)
    3. Sensor properties (sensor name, dpi/cpi, max acceleration, max speed)
    4. Wireless properties (rgb-on/average battery life, rgb-off/max battery life)
    5. Whether the mouse is RGB
6. Upload each mouse listing to MongoDB