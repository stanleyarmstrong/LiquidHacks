import os
import json
from typing import Tuple, List

from pymongo import MongoClient
from pathlib import Path

from scrapy import Spider
from scrapy.crawler import CrawlerProcess

SPIDERS_AND_PATHS = [('./scrapers/hyperx_mice.py', './cache/hyperx.json'),
                     ('./scrapers/logitechg_mice.py', './cache/logitechg.json'),
                     ('./scrapers/steelseries_mice.py', './cache/steelseries.json')]

def upload_mouse_specs(mongo_client, mongo_db, mongo_collection, json_file):
    db = mongo_client[mongo_db]
    collection = db[mongo_collection]

    with open(Path(json_file)) as f:
        data = json.load(f)

    for mouse in data:
        print(mouse['name'])
        collection.find_one_and_replace(
            {'name': mouse['name']},
            mouse,
            upsert=True)


def run_crawler(spider_py, json_file='./cache/popularity.json'):
    json_path = Path(json_file)

    os.makedirs(os.path.dirname(json_path), exist_ok=True)

    with open(json_path, 'w') as jf:
        jf.truncate(0)

    os.system(f"scrapy runspider {spider_py} -o {json_file}")

def run_crawlers(spiders_and_paths):
    # Expecting list of tuples os scrapy spider file names and output paths

    for spider, json_path in spiders_and_paths:
        run_crawler(spider, json_path)

if __name__ == "__main__":
    username = os.getenv('MONGO_USER')
    password = os.getenv('MONGO_PASS')

    client = MongoClient(f"mongodb+srv://{username}:{password}@liquidmouse.8pyh5.mongodb.net")

    run_crawlers(SPIDERS_AND_PATHS)

    for spider, json_file in SPIDERS_AND_PATHS:

        upload_mouse_specs(client, "MouseData", "products", json_file)
