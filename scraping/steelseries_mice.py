from typing import List

import re
import scrapy


class SteelseriesMiceSpider(scrapy.Spider):
    name = 'steelseries_mice'
    allowed_domains = ['steelseries.com']
    start_urls = ['https://steelseries.com/gaming-mice']

    def parse(self, response):

        mice_elems = response.css('div.catalog-list-item')

        for mouse_elem in mice_elems:

            name = mouse_elem.css('h2.catalog-list-product__name.OneLinkNoTx::text').extract_first()

            if name is not None:
                name = name.strip()
                product_url = response.urljoin(mouse_elem.css('a.catalog-list-product__link').attrib['href'])

                mouse = {
                    "name": name,
                    "display_name": name,
                    "product_url": product_url,
                    "brand": "Steelseries"
                }

                # Scrape the individual mouse's product page
                yield scrapy.Request(
                    url=product_url,
                    meta={'mouse': mouse},
                    callback=self.parse_mouse_details
                )

    def parse_mouse_details(self, response):

        mouse = response.meta.get('mouse')
        spec_rows = response.css('div.data-point.row')

        # Have to do this because of newlines IN the product name

        specs = {}
        mouse['specs'] = specs

        # https://support.steelseries.com/hc/en-us/articles/221391568-What-does-my-warranty-cover-and-how-long-does-it-last-
        specs['warranty_length'] = 1

        for spec_row in spec_rows:
            row_title = spec_row.css('h4.data-point__label::text').extract_first()
            row_value = spec_row.css('p.data-point__value::text').extract_first()

            if row_title is not None and row_value is not None:

                row_title = row_title.strip()
                row_value = row_value.strip()

                #self.log(f"{row_title}: {row_value}")

                if row_title == "Height":
                    specs['height'] = re.search(r"[0-9]*\.?[0-9]+", row_value).group(0).strip()

                elif row_title == "Width":
                    specs['width'] = re.search(r"[0-9]*\.?[0-9]+", row_value).group(0).strip()

                elif row_title == "Length":
                    specs['depth'] = re.search(r"[0-9]*\.?[0-9]+", row_value).group(0).strip()

                elif row_title == "Weight":
                    specs['weight'] = re.search(r"[0-9]*\.?[0-9]+", row_value).group(0).strip()

                elif "Cable Length" in row_title:
                    specs['cable_length'] = re.search(r"[0-9]*\.?[0-9]+", row_value).group(0)

                elif row_title == "Polling Rate":
                    polling_rate = re.search(r"[0-9]+(?=Hz)", row_value)
                    if polling_rate is None:
                        specs['polling_rate'] = str(int(re.search(r"[0-9]+", row_value).group(0)) * 1000)
                    else:
                        specs['polling_rate'] = polling_rate.group(0)

                elif row_title == "Sensor" or row_title == "Primary Sensor":
                    specs['sensor'] = row_value

                elif row_title == "CPI":
                    specs['min_dpi'] = re.search(r"[0-9]+(?=–)", row_value).group(0)
                    specs['max_dpi'] = re.search(r"(?<=–)[0-9]*,?[0-9]+", row_value).group(0)

                elif row_title == "Acceleration":
                    specs['max_acceleration'] = re.search(r"[0-9]+", row_value).group(0)

                elif row_title == "IPS":
                    specs['max_speed'] = re.search(r"[0-9]+", row_value).group(0)

                elif row_title == "Battery Life":
                    specs['wireless'] = True
                    specs['avg_battery_life'] = re.search(r"[0-9]+", row_value).group(0)
                    specs['max_battery_life'] = specs['avg_battery_life']

                elif row_title == "Illumination":
                    specs['rgb'] = True

                elif row_title == "Shape":
                    if row_value == "Ambidextrous":
                        specs['hand'] = "ambidextrous"
                    else:
                        specs['hand'] = "right"

                elif row_title == "Number of Buttons":
                    specs['programmable_buttons'] = row_value

        yield mouse
