# -*- coding: utf-8 -*-
import scrapy
import re
from indeed.items import IndeedJobItem

class IndeedSpider(scrapy.Spider):
    name = 'indeed_spider'
    allowed_domains = ['indeed.com']
    start_urls = ['https://www.indeed.com/q-data-scientist-l-New-York,-NY-jobs.html']

    def parse(self, response):

        jobs_on_page = response.xpath("//td[@id='resultsCol']").xpath("./div[@data-tn-component='organicJob']")

        for job in jobs_on_page:
            job_to_save  = IndeedJobItem()

            location = job.xpath("./span[@class='location']/text()").extract_first().split(",")

            job_to_save['title'] = job.xpath("./h2/a/@title").extract_first()
            job_to_save['city'] = location[0].strip()
            job_to_save['region'] = ''.join(re.findall('[a-zA-Z]+', location[1]))
            job_to_save['region_code'] = ''.join(re.findall('\d+', location[1]))
            job_to_save['company'] = ''.join(job.xpath(".//span[@class='company']//text()").extract()).strip()

            yield job_to_save
