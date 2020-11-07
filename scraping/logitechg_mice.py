from typing import List

from gaming_mouse import *
import re


import scrapy


class LogitechgMiceSpider(scrapy.Spider):
    name = 'logitechg_mice'
    allowed_domains = ['logitechg.com']
    start_urls = ['http://www.logitechg.com/en-us/products/gaming-mice.html']

    def parse(self, response):

        mice_elems = response.css('div.product')

        for mouse_elem in mice_elems:

            name = mouse_elem.attrib['data-product-name']
            product_url = response.urljoin(mouse_elem.css('a.img-link').attrib['href'])

            if 'bundle' not in name:

                mouse = {
                    "name": name
                    "product_url": product_url
                }

                # Scrape the individual mouse's product page
                yield scrapy.Request(
                    url=product_url,
                    meta={'mouse': mouse},
                    callback=self.parse_mouse_details
                )

                self.log(f"Found mouse \"{name}\" with product URL \"{product_url}\"")

                yield {
                    "product_name": name,
                    "product_url": product_url
                }

    def parse_mouse_details(self, response):

        mouse = response.meta.get('mouse', {})
        spec_lists = response.css('div.list-information')

        specs = {}

        physical_specs = None
        misc_specs = None
        responsiveness_specs = None
        warranty_specs = None
        tracking_specs = None
        battery_specs = None

        for spec_list in spec_lists:
            list_title = response.css('h6.specs-group-title::text').extract_first().strip().toupper()

            if list_title == "PHYSICAL SPECIFICATIONS":
                physical_specs = spec_list

            elif list_title == "RESPONSIVENESS":
                responsiveness_specs = spec_list

            elif list_title == "WARRANTY INFORMATION":
                warranty_specs = spec_list

            elif list_title == "TRACKING":
                tracking_specs = spec_list

            elif list_title == "BATTERY LIFE":
                battery_specs = spec_list

            elif list_title == "TECHNICAL SPECIFICATIONS"\
                    or list_title == "OTHER FEATURES":
                misc_specs = spec_list


        if physical_specs is not None:

            for spec in physical_specs.css('li::text'):
                if "Height" in spec:
                    specs['height'] = re.match(r"[0-9]+\.[0-9]+(?= mm)", spec)

                elif "Width" in spec:
                    specs['width'] = re.match(r"[0-9]+\.[0-9]+(?= mm)", spec)

                elif "Depth" in spec:
                    specs['depth'] = re.match(r"[0-9]+\.[0-9]+(?= mm)", spec)

                elif "Weight" in spec:
                    specs['weight'] = re.match(r"[0-9]+(?= g)", spec)

                elif "Cable length" in spec:
                    specs['cable_length'] = re.match(r"[0-9]+\.[0-9]+(?= m)", spec)

        if misc_specs is not None:

            for spec in misc_specs.css('li::text'):
                if "RGB" in spec:
                    specs['rgb'] = True

                elif "ambidextrous" in spec:
                    specs['ambidextrous'] = True

                elif "programmable buttons" in spec:
                    specs['programmable_buttons'] =