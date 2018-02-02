# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class DatabaseItem(scrapy.Item):
    # define the fields for your item here like:
    id = scrapy.Field()
    model = scrapy.Field()
    price = scrapy.Field()
    detail = scrapy.Field()