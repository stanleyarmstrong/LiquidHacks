import re
import scrapy

class HyperXMiceSpider(scrapy.Spider):
    name = 'hyperx_mice'
    allowed_domains = ['hyperxgaming.com']
    start_urls = ['https://www.hyperxgaming.com/unitedstates/us/mice']

    def parse(self, response):

        mice_elems = response.css('div.c-category')

        for mouse_elem in mice_elems:

            name = mouse_elem.css('h4.txt-mega::text').extract_first().strip()
            product_url = response.urljoin(mouse_elem.css('a.btn').attrib['href'])

            mouse = {
                "name": name,
                "display_name": name,
                "product_url": product_url,
                "brand": "HyperX"
            }

            # Scrape the individual mouse's product page
            yield scrapy.Request(
                url=product_url,
                meta={'mouse': mouse},
                callback=self.parse_mouse_details
            )

    def parse_mouse_details(self, response):

        mouse = response.meta.get('mouse')
        spec_rows = response.css('div.c-table').css('tr')
        img = response.css('div.feature-image-slides').css('img').attrib['src']

        specs = {}
        mouse['specs'] = specs
        mouse['product_img'] = img

        # https://support.steelseries.com/hc/en-us/articles/221391568-What-does-my-warranty-cover-and-how-long-does-it-last-
        specs['warranty_length'] = 2

        # Ignore header row
        for spec_row in spec_rows:
            row = spec_row.css('td::text').extract()
            if len(row) > 1:
                row_title = row[0].strip()
                row_value = ''.join(row[1:])

                row_title = row_title.strip()
                row_value = row_value.strip()

                # self.log(f"{row_title}: {row_value}")

                if row_title.startswith("Dimensions"):
                    #self.log(row_value)
                    height_str = re.search(r"H.*: [0-9]*\.?[0-9]+", row_value).group(0)
                    width_str = re.search(r"W.*: [0-9]*\.?[0-9]+", row_value).group(0)
                    length_str = re.search(r"L.*: [0-9]*\.?[0-9]+", row_value).group(0)
                    specs['height'] = re.search(r"[0-9]*\.?[0-9]+", height_str).group(0)
                    specs['width'] = re.search(r"[0-9]*\.?[0-9]+", width_str).group(0)
                    specs['depth'] = re.search(r"[0-9]*\.?[0-9]+", length_str).group(0)

                    cable_length = re.search(r"(?<=Cable length: )[0-9]*\.?[0-9]+", row_value)
                    if cable_length is not None:
                        specs['cable_length'] = cable_length.group(0)

                elif row_title.startswith("Length"):
                    specs['depth'] = re.search(r"[0-9]*\.?[0-9]+", row_value).group(0)

                elif row_title.startswith("Height"):
                    specs['height'] = re.search(r"[0-9]*\.?[0-9]+", row_value).group(0)

                elif row_title.startswith("Width"):
                    specs['width'] = re.search(r"[0-9]*\.?[0-9]+", row_value).group(0)

                elif row_title.startswith("Cable length"):
                    specs['cable_length'] = re.search(r"[0-9]*\.?[0-9]+", row_value).group(0)

                elif row_title.startswith("Weight (without cable)"):
                    specs['weight'] = re.search(r"[0-9]*\.?[0-9]+", row_value).group(0).strip()

                elif row_title.startswith("Polling rate"):
                    specs['polling_rate'] = re.search(r"[0-9]+(?=Hz)", row_value).group(0)

                elif row_title.startswith("Sensor"):
                    specs['sensor'] = row_value

                elif row_title.startswith("Resolution"):
                    specs['max_dpi'] = re.search(r"[0-9]*,?[0-9]+", row_value).group(0)

                elif row_title.startswith("DPI Presets"):
                    specs['min_dpi'] = re.search(r"[0-9]+", row_value).group(0)

                elif row_title.startswith("Acceleration"):
                    specs['max_acceleration'] = re.search(r"[0-9]+", row_value).group(0)

                elif row_title.startswith("Speed"):
                    specs['max_speed'] = re.search(r"[0-9]+", row_value).group(0)

                elif "Battery Life" in row_title:
                    specs['wireless'] = True
                    specs['avg_battery_life'] = re.search(r"[0-9]+(?= hours – Default)", row_value).group(0)
                    specs['max_battery_life'] = re.search(r"[0-9]+(?= hours - LED off)", row_value).group(0)

                elif row_title.startswith("Light effects"):
                    specs['rgb'] = True

                elif row_title.startswith("Shape"):
                    if row_value == "Symmetrical":
                        specs['hand'] = "ambidextrous"
                    else:
                        specs['hand'] = "right"

                elif row_title.startswith("Buttons"):
                    specs['programmable_buttons'] = row_value

        yield mouse