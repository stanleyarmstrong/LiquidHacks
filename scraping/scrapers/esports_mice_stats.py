from typing import List

import re
import scrapy


class EsportsLocalStatsSpider(scrapy.Spider):
    name = 'esports_mice_stats'
    start_urls=['file:///D:/Github/LiquidHacks/scraping/cache/stats_0.html', 'file:///D:/Github/LiquidHacks/scraping/cache/stats_1.html', 'file:///D:/Github/LiquidHacks/scraping/cache/stats_2.html']

    def __init__(self, *args, **kwargs):  # <-- filename
        super().__init__(*args, **kwargs)

        if 'filenames' in kwargs:
            self.start_urls = kwargs['filenames']

        if 'player_column' in kwargs:
            self.player_column = kwargs['player_column']
        else:
            self.player_column = 1

        if 'mouse_column' in kwargs:
            self.mouse_column = kwargs['player_column']
        else:
            self.mouse_column = 14

    def parse(self, response):
        self.log("Hello world")
        rows = response.css('tr')

        mouse_stats = {}

        for row in rows[1:]:
            self.log(row)
            columns = row.css('td')

            if len(columns) >= 15:
                player_elem = columns[self.player_column].css('a::text').extract_first()
                mouse_elem = columns[self.mouse_column].css('b::text').extract_first()

                if player_elem is not None and mouse_elem is not None:
                    player = player_elem.strip()
                    mouse = mouse_elem.strip()
                    #self.log(mouse)

                    mouse_dict = mouse_stats.setdefault(mouse, {'name':mouse, 'count':0, 'players':[]})
                    mouse_dict['count'] += 1
                    mouse_dict['players'].append(player)

        for mouse_dict in mouse_stats.values():
            yield mouse_dict