import scrapy
import re


class RazerMiceSpider(scrapy.Spider):
    name = 'razer_mice'
    allowed_domains = ['razer.com']
    start_urls = ['https://www.razer.com/shop/mice/gaming-mice?query=:newest:category:mice-mice']

    def parse(self, response):

        mice_elems = response.css('div.grid-item')

        for mouse_elem in mice_elems:
            mouse = {}

            mouse['name'] = mouse_elem.css('a.text-white::text').extract()
            mouse['img_url'] = mouse_elem.css('img.ng-star-inserted').attrib['src']
            mouse['price'] = mouse_elem.css('span.final-price::text').extract()
            mouse['warranty_length'] = 2
            self.log(mouse['price'])
            mouse['product_url'] = response.urljoin(mouse_elem.css('a.text-razer-green').attrib['href'])
            # Scrape the individual mouse's product page
            yield scrapy.Request(
                url=mouse['product_url'],
                meta={'mouse': mouse},
                callback=self.parse_mouse_details
            )

    def parse_mouse_details(self, response):

        mouse = response.meta.get('mouse')
        spec_lists = response.css('tr')
        specs = {}
        mouse['specs'] = specs
        for spec in spec_lists:
            spec_category = spec.css('th::text').extract()[0].lower()
            val = spec.css('td::text').extract_first()
            if val is None:
                continue
            else:
                val = val.lower()
            self.log(val)
            if spec_category == 'form factor':
                if 'ambidextrous' in val:
                    specs['ambidextrous'] = 'ambidextrous'
                elif 'left' in val:
                    specs['hand'] = 'left'
                else:
                    specs['hand'] = 'right'
            if spec_category == 'connectivity':
                if 'wireless' in val:
                    specs['wireless'] = True
                else:
                    specs['wireless'] = False
            if spec_category == 'rgb lighting':
                if 'rgb' in val:
                    specs['rgb'] = True
                else:
                    specs['rgb'] = False
            if spec_category == 'battery life':
                specs['max_battery_life'] = re.search(r"[0-9]+", val)
            if spec_category == 'sensor':
                specs['sensor'] = val
            if spec_category == 'max sensitivity(dpi)':
                specs['max_dpi'] = val
                specs['min_dpi'] = val
            if spec_category == 'programmable buttons':
                specs['programmable_buttons'] = val
            if spec_category == 'max speed(ips)':
                specs['max_speed'] = val
            if spec_category == 'max acceleration(g)':
                specs['max_acceleration'] = val
            if spec_category == 'weight':
                specs['weight'] = re.search(r"[0-9]+ ?(?=g)")
            if spec_category == 'sizes':
                sizes = re.match(r"[0-9]+.[0-9]+ ?(?=mm)", val)
                specs['depth'] = sizes[0]
                specs['width'] = sizes[1]
                specs['height'] = sizes[2]
            

            



        yield mouse