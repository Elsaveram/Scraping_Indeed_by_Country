# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class IndeedJobItem(scrapy.Item):
    # define the fields for your item here like:
    title = scrapy.Field()
    company = scrapy.Field()
    city = scrapy.Field()
    region = scrapy.Field()
    region_code = scrapy.Field()
    company = scrapy.Field()
    how_long_open = scrapy.Field()
    number_of_reviews = scrapy.Field()
    rating = scrapy.Field()
    summary = scrapy.Field()
