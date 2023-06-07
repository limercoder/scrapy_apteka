import requests
from datetime import datetime
from bs4 import BeautifulSoup
import scrapy
import json
from urllib.parse import urlparse
import os
import random
dir = "data"
os.makedirs(dir)
class MySpider(scrapy.Spider):
    name = "Apteka"
    def start_requests(self):
        urls = [
            "https://apteka-ot-sklada.ru/catalog/medikamenty-i-bady/anesteziya-i-rastvoriteli",
            "https://apteka-ot-sklada.ru/catalog/hozyaystvennye-tovary/bytovaya-himiya",
            "https://apteka-ot-sklada.ru/catalog/meditsinskaya-tekhnika/gigiena-nosa"
        ]


        for url in urls:
            yield scrapy.Request(url, callback=self.parse_category) #meta={"proxy": "http://158.51.107.253:8080"}) # нужно найти белые бесплатные прокси...
    def parse_category(self, response):
        import time
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Max-Age': '3600',
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0'
        }
        xpath_names = '//div[contains(@class, "goods-card__name")]/a/span[@itemprop="name"]/text()'
        price_xpath = '//span[contains(@class, "goods-card__cost")]/text()'
        rpc_ids = response.css('.goods-card__link::attr(href)').getall()
        country = response.css('.goods-card__producer.text span[itemtype="location"]::text').get()
        names = response.xpath(xpath_names).getall()
        brand = response.xpath('//span[@itemtype="legalName"]/text()').get()
        prices = response.xpath(price_xpath).getall()
        available = response.css('div.goods-card__not-available::text').get()
        sectioN = response.css("li.ui-pagination__page > a.ui-pagination__link.ui-pagination__link_number::attr(href)").get()
        Section = urlparse(sectioN)
        section = Section.path.split("/")[2:]
        decoded_parts = [part.split("%2F") for part in section ]
        decoded_section = [part for sublist in decoded_parts for part in sublist]
        city = response.css('.ui-link.ui-link_theme_primary span.ui-link__text::text').get()
        image_url = response.css("div.ui-card__preview img::attr(src)").get()

        if available is None:
            ab = "True"
        else:
            ab = "0"
        for name, price, link in zip(names, prices, rpc_ids):
            price = price.strip().replace("₽", " ")
            complete_link = "https://apteka-ot-sklada.ru"+link
            complete_img = "https://apteka-ot-sklada.ru"+image_url
            req = requests.get(complete_link, headers=headers)
            content = req.text
            soup = BeautifulSoup(content, "html.parser")
            description = soup.find("div", class_="custom-html content-text").get_text(strip=True)
            rpc = link.split("_")[-1]
            city = city.strip()
            t = datetime.now()
            Time = t.isoformat()
            data = {
                "timestamp": Time,
                "RPC": rpc,
                "url": complete_link,
                "title": name,
                "marketing_tags": [],
                "brand": brand,
                "section": decoded_section,
                "price_data": {
                    "current": price,
                    "original": price,
                    "sale_tag": "Не нашел товары со скидкой"

                },
                "stock": {
                    "in_stock": ab,
                    "count": 0,
                    "location": city
                },
                "assets": {
                    "main_image": complete_img,
                    "set_images": [0], # Нет изображений кроме главной картинки
                    "view360": [0],
                    "video": [0]
                },
                "metadata": {
                    "__description": description,
                    "АРТИКУЛ": "Не увидел товары где указан артикул",
                    "СТРАНА ПРОИЗВОДИТЕЛЬ": country
                },
                "variants": 1 # Перерыл огромное количество товаров не было там вариантов кроме 1. Можете отправить мне ссылку на такие
            }

            json_object = json.dumps(data, indent=4, ensure_ascii=False)

            data = ["a", "v", "z", "b", "s", "c", "f", "i", "m", "t"]
            r = random.choice(data)
            v = random.choice(data)
            i = random.choice(data)

            name_json = (r+"data"+i+v+".json")
            file_path = os.path.join(dir, name_json)
            with open(file_path, "w") as file:
                try:
                   file.write(json_object)
                except:
                    pass
                time.sleep(1)

