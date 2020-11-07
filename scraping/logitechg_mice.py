from typing import List

from gaming_mouse import *
import re


import scrapy


class LogitechgMiceSpider(scrapy.Spider):
    name = 'logitechg_mice'
    allowed_domains = ['logitechg.com']
    start_urls = ['https://www.logitechg.com/en-us/products/gaming-mice.html']

    def parse(self, response):

        mice_elems = response.css('div.product')

        for mouse_elem in mice_elems:

            name = mouse_elem.attrib['data-product-name']
            product_url = response.urljoin(mouse_elem.css('a.img-link').attrib['href'])

            if 'bundle' not in name:

                mouse = {
                    "name": name,
                    "product_url": product_url
                }

                # Scrape the individual mouse's product page
                yield scrapy.Request(
                    url=product_url,
                    meta={'mouse': mouse},
                    callback=self.parse_mouse_details
                )

    def parse_mouse_details(self, response):

        mouse = response.meta.get('mouse')
        spec_lists = response.css('div.specs-group')
        img_url = response.css('div.product-shot-ctn').css('img').attrib['src']
        product_name = response.css('div.product-details-title::text')

        # Have to do this because of newlines IN the product name
        mouse['display_name'] = ' '.join(product_name.extract_first().split())
        mouse['product_img'] = img_url

        specs = {}
        mouse['specs'] = specs

        physical_specs = None
        responsiveness_specs = None
        warranty_specs = None
        tracking_specs = None
        battery_specs = None
        misc_specs = None

        #self.log(f"found {len(spec_lists)} spec lists")

        for spec_list in spec_lists:
            list_header = spec_list.css('h6.specs-group-title::text').extract_first()

            # if list_header is None:
            #     self.log("Didn't find a title for this list:")
            #     self.log(spec_list)

            if list_header is not None:
                list_title = list_header.strip().upper()

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

                elif list_title == "TECHNICAL SPECIFICATIONS" \
                        or list_title == "OTHER FEATURES":
                    misc_specs = spec_list


        if physical_specs is not None:

            for spec in physical_specs.css('li::text').extract():
                if "Height" in spec:
                    specs['height'] = re.search(r"[0-9]*\.?[0-9]+ ?(?=mm)", spec).group(0).strip()

                elif "Width" in spec:
                    specs['width'] = re.search(r"[0-9]*\.?[0-9]+ ?(?=mm)", spec).group(0).strip()

                elif "Depth" in spec:
                    specs['depth'] = re.search(r"[0-9]*\.?[0-9]+ ?(?=mm)", spec).group(0).strip()

                elif "Weight" in spec:
                    specs['weight'] = re.search(r"[0-9]+(?= g)", spec).group(0)

                elif "Cable length" in spec:
                    specs['cable_length'] = re.search(r"[0-9]*\.?[0-9]+(?= m)", spec).group(0)


        if responsiveness_specs is not None:

            for spec in responsiveness_specs.css('li::text').extract():
                if "USB report rate" in spec:
                    specs['polling_rate'] = re.search(r"[0-9]+(?= Hz)", spec).group(0)

        if tracking_specs is not None:

            for spec in tracking_specs.css('li::text').extract():

                if "Sensor" in spec:
                    specs['sensor'] = re.search(r"(?<=Sensor: ).+", spec).group(0).strip()

                elif "dpi" in spec:
                    specs['min_dpi'] = re.search(r"(?<=Resolution: )[0-9]+", spec).group(0)
                    specs['max_dpi'] = re.search(r"[0-9]*,?[0-9]+(?= dpi)", spec).group(0)

                elif "Max. acceleration" in spec:
                    specs['max_acceleration'] = re.search(r"[0-9]+", spec).group(0)

                elif "Max. speed" in spec:
                    specs['max_speed'] = re.search(r"[0-9]+", spec).group(0)

        if battery_specs is not None:

            specs['wireless'] = True

            for spec in tracking_specs.css('li::text').extract():

                if "Default lighting" in spec:
                    specs['avg_battery_life'] = re.search(r"[0-9]+(?= hours)", spec).group(0)

                if "No lighting" in spec:
                    specs['max_battery_life'] = re.search(r"[0-9]+(?= hours)", spec).group(0)

        if warranty_specs is not None:

            for spec in warranty_specs.css('li::text').extract():
                warranty_length = re.search(r"[0-9]+(?=-Year)", spec)

                if warranty_length is not None:
                    specs['warranty_length'] = warranty_length.group(0)

        if misc_specs is not None:

            for spec in misc_specs.css('li::text').extract():
                if "RGB" in spec:
                    specs['rgb'] = True

                elif "ambidextrous" in spec:
                    specs['hand'] = "ambidextrous"

                elif "programmable buttons" in spec:
                    specs['programmable_buttons'] = re.search(r"[0-9]+(?= programmable)", spec).group(0)

                elif "dpi" in spec:
                    specs['min_dpi'] = re.search(r"(?<=Resolution: )[0-9]+(?= -)", spec).group(0)
                    specs['max_dpi'] = re.search(r"[0-9]*,?[0-9]+(?= dpi)", spec).group(0)

        yield mouse