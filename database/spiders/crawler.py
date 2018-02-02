# -*- coding: utf-8 -*-
import scrapy
from database.items import DatabaseItem
import lxml
import urllib
from bs4 import BeautifulSoup


class CrawlerSpider(scrapy.Spider):
    name = 'crawler'
    allowed_domains = ['phongvu.vn']
    start_urls = 'https://phongvu.vn/'

    counter = 0
    max_page = 1
    index = 0

    def extract_text(self, str):
        soup = BeautifulSoup(str)

        # kill all script and style elements
        for script in soup(["script", "style"]):
            script.extract()  # rip it out

        # get text
        text = soup.get_text()

        # break into lines and remove leading and trailing space on each
        lines = (line.strip() for line in text.splitlines())
        # break multi-headlines into a line each
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        # drop blank lines
        text = '\n'.join(chunk for chunk in chunks if chunk)

        if '\n- ' not in text:
            text = text.replace('- ', '\n')
        else:
            text = text.replace('- ', '')

        return text

    def start_requests(self):
        urls = []
        base_url = 'https://phongvu.vn/may-tinh-xach-tay/laptop-doanh-nhan/'
        articles = ['asus.html',
                    'dell.html',
                    'macbook.html',
                    'hp.html',
                    'lenovo.html',
                    'acer.html'
                    ]

        for item in articles:
            self.counter = 0
            while self.counter < self.max_page:
                self.counter += 1
                urls.append(base_url + item + '?p=' + str(self.counter))

        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse_news)

    def parse_news(self, response):

        ARTICLE_SELECTOR = '//div[contains(@class,"grid-view")]'
        for row in response.xpath(ARTICLE_SELECTOR).extract():
            if row.strip():
                row = lxml.html.fromstring(row)
                title = next(iter(row.xpath('//a[contains(@class,"grid-view-product-name")]/@href')), "").strip()

                title = title.replace('https://phongvu.vn/','')
                yield scrapy.Request(url=self.start_urls + title, callback=self.parse_news_v2)


    def parse_news_v2(self, response):
        MODEL_SELECTOR = '//div[contains(@class,"detail-product-name")]/text()'
        PRICE_SELECTOR = '//div[contains(@class,"detail-product-final-price")]/text()'
        DETAIL_SELECTOR = '//div[contains(@class,"detail-product-desc-content")]'

        for row in response.xpath(DETAIL_SELECTOR).extract():
            model = response.xpath(MODEL_SELECTOR).extract()[0].strip()
            price = response.xpath(PRICE_SELECTOR).extract()[0].strip()
            detail = self.extract_text(row.strip())

            if detail:
                self.index += 1
                item = DatabaseItem()
                item['id'] = self.index
                item['model'] = model
                item['price'] = price
                item['detail'] = detail
                yield item
