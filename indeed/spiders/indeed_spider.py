# -*- coding: utf-8 -*-
import scrapy


class IndeedSpiderSpider(scrapy.Spider):
    name = 'indeed_spider'
    allowed_domains = ['indeed.com']
    start_urls = ['http://indeed.com/']

    def parse(self, response):
        pass
