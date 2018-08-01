# -*- coding: utf-8 -*-
from scrapy import Spider, Request
import re
from indeed.items import IndeedJobItem

class IndeedSpider(Spider):
    name = 'indeed_spider'
    allowed_domains = ['indeed.com']
    start_urls = ['https://www.indeed.com/q-data-scientist-l-New-York,-NY-jobs.html']

    def parse(self, response):
        jobs_on_page = response.xpath("//td[@id='resultsCol']").xpath("./div[@data-tn-component='organicJob']")

        for job in jobs_on_page:
            job_to_save = {}

            location = job.xpath("./span[@class='location']/text()").extract_first().split(",")
            link_to_job_detail = "https://www.indeed.com" + job.xpath("./h2/a/@href").extract_first()

            job_to_save['title'] = job.xpath("./h2/a/@title").extract_first()
            job_to_save['city'] = location[0].strip()
            job_to_save['region'] = ''.join(re.findall('[a-zA-Z]+', location[1]))
            job_to_save['region_code'] = ''.join(re.findall('\d+', location[1]))
            job_to_save['company'] = ''.join(job.xpath(".//span[@class='company']//text()").extract()).strip()

            yield Request(url=link_to_job_detail, meta=job_to_save, callback=self.parse_job_detail_page)


    def parse_job_detail_page(self, response):
       job_to_save = IndeedJobItem()
       job_to_save = response.meta

       #job_to_save['rating']
       #job_to_save['reports_to']
       #job_to_save['number_of_reviews']
       #job_to_save['description']
       #job_to_save['how_long_open']

       yield job_to_save
