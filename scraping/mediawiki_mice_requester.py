import json
import os
import time
import requests
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

JSON_FILE = "./popularity.json"

# Comply to the liquidhacks TOS
HEADERS = {'user-agent': 'liquidhacks-mouse-ranker/0.0.1 (Hydroptix#1869; frazee.samuel@gmail.com)', 'Accept-Encoding': 'gzip' }
RATE_LIMIT = 30

if __name__ == "__main__":
    files = 0
    html_paths = []
    for page in PAGE_REQUESTS:
        print(f"requesting \"{page}\"")

        response = requests.get(page, headers=HEADERS)

        if response.status_code == 429:
            print("Rate limited, visit liquipedia.net to get unblocked")
            exit(response.status_code)
        else:
            html = response.json()['parse']['text']['*']

        file_path = Path(f'./cache/stats_{files}.html')
        html_paths.append(file_path.resolve().as_uri())
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w', encoding="utf-8") as f:
            f.truncate(0)
            f.write(html)

        files += 1

        time.sleep(RATE_LIMIT)

    with open(JSON_FILE, 'w') as jf:
        jf.truncate(0)

    # Save output from the crawler to the JSON file
    process = CrawlerProcess(settings={
        "FEEDS": {
            JSON_FILE: {"format": "json"},
        },
    })

    # Run the crawler
    process.crawl(EsportsLocalStatsSpider, filenames=html_paths)
    process.start()

    total_stats = {}

    # Read the JSON from the file
    with open(Path(JSON_FILE)) as f:
        data = json.load(f)

    # combine all the entries in the JSON file
    for mouse_json in data:
        mouse_dict = total_stats.setdefault(mouse_json['name'], {'name': mouse_json['name'], 'count': 0, 'players': []})
        mouse_dict['count'] += mouse_json['count']
        mouse_dict['players'].extend(mouse_json['players'])

    # Add all mouse counts to mongodb
    username = os.getenv('MONGO_USER')
    password = os.getenv('MONGO_PASS')

    dbname = "MouseData"
    collectionname = "popularity"

    client = MongoClient(f"mongodb+srv://{username}:{password}@liquidmouse.8pyh5.mongodb.net")
    db = client[dbname]
    test_collection = db[collectionname]

    for popularity_dict in total_stats.values():
        test_collection.find_one_and_replace({'name': popularity_dict['name']}, popularity_dict, upsert=True)
