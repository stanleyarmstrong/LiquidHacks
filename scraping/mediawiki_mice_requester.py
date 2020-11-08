import json
import os
import time
import requests
from hashlib import sha256
from pathlib import Path

from pymongo import MongoClient
from scrapy.crawler import CrawlerProcess
from scrapers.esports_mice_stats import EsportsLocalStatsSpider

# Overwatch not included because its table has an inconsistent number of columns
PAGE_REQUESTS = [
    'https://liquipedia.net/counterstrike/api.php?action=parse&page=List of player mouse settings/001-400&prop=text&section=1&format=json',
    'https://liquipedia.net/counterstrike/api.php?action=parse&page=List of player mouse settings/401-800&prop=text&section=1&format=json',
    'https://liquipedia.net/counterstrike/api.php?action=parse&page=List of player mouse settings/801-1200&prop=text&section=1&format=json',
    'https://liquipedia.net/valorant/api.php?action=parse&page=List of player mouse settings&prop=text&section=0&format=json',
    'https://liquipedia.net/apexlegends/api.php?action=parse&page=List of player mouse settings&prop=text&section=0&format=json']

JSON_FILE = "popularity.json"

# Comply to the liquidhacks TOS
HEADERS = {'user-agent': 'liquidhacks-mouse-ranker/0.0.1 (Hydroptix#1869; frazee.samuel@gmail.com)',
           'Accept-Encoding': 'gzip'}


def update_cache(mediawiki_requests=None, cache_dir="./cache", rate_limit=30, request_headers=None, force=False):
    if mediawiki_requests is None:
        mediawiki_requests = PAGE_REQUESTS

    if request_headers is None:
        request_headers = HEADERS

    html_paths = []
    for page in PAGE_REQUESTS:

        # Get a unique hash for this request to identify the file
        request_hash = sha256(bytes(page, "utf-8")).hexdigest()

        file_path = Path(f'{cache_dir}/{request_hash}.html')

        if force or not file_path.exists():

            response = requests.get(page, headers=HEADERS)

            if response.status_code == 429:
                print("Rate limited, visit liquipedia.net to get unblocked")
                return(response.status_code)
            else:
                html = response.json()['parse']['text']['*']

            html_paths.append(file_path.resolve().as_uri())
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w', encoding="utf-8") as f:
                f.truncate(0)
                f.write(html)

            time.sleep(rate_limit)


def process_cache(cache_dir="./cache", json_file='popularity.json'):
    json_path = Path(json_file)
    cache_path = Path(cache_dir)

    with open(json_path, 'w') as jf:
        jf.truncate(0)

    # Save output from the crawler to the JSON file
    process = CrawlerProcess(settings={
        "FEEDS": {
            str(json_path): {"format": "json"},
        },
    })

    html_paths = [str(x.absolute().as_uri()) for x in cache_path.glob('*.html')]

    # Run the crawler
    process.crawl(EsportsLocalStatsSpider, filenames=html_paths)
    process.start()


def upload_popularity_stats(mongo_client, mongo_db, mongo_collection, json_file='popularity.json'):
    db = mongo_client[mongo_db]
    collection = db[mongo_collection]

    # Read the JSON from the file
    with open(Path(json_file)) as f:
        data = json.load(f)

    # combine all the entries in the JSON file
    total_stats = {}
    for mouse_json in data:
        mouse_dict = total_stats.setdefault(mouse_json['name'], {'name': mouse_json['name'], 'count': 0, 'players': []})
        mouse_dict['count'] += mouse_json['count']
        mouse_dict['players'].extend(mouse_json['players'])

    # Update all mouse counts in mongodb
    for popularity_dict in total_stats.values():
        collection.find_one_and_replace({'name': popularity_dict['name']}, popularity_dict, upsert=True)


if __name__ == "__main__":
    username = os.getenv('MONGO_USER')
    password = os.getenv('MONGO_PASS')
    mongo_client = MongoClient(f"mongodb+srv://{username}:{password}@liquidmouse.8pyh5.mongodb.net")

    update_cache()
    process_cache()
    upload_popularity_stats(mongo_client, 'MouseData', 'popularity')
