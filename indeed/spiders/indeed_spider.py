# -*- coding: utf-8 -*-
import scrapy
from indeed.items import IndeedJobItem

class IndeedSpider(scrapy.Spider):
    name = 'indeed_spider'
    allowed_domains = ['indeed.com']
    start_urls = ['https://www.indeed.com/q-data-scientist-l-New-York,-NY-jobs.html']

    def parse(self, response):

        jobs_on_page = response.xpath("//td[@id='resultsCol']").xpath("./div[@data-tn-component='organicJob']")

        for job in jobs_on_page:
            job_to_save  = IndeedJobItem()
            job_to_save['title'] = job.xpath("./h2/a/text()").extract_first()
            print(job_to_save['title'])
            yield job_to_save
