# -*- coding: utf-8 -*-
from scrapy import Spider, Request
import re
from indeed.items import IndeedJobItem

class IndeedSpider(Spider):
    name = 'indeed_spider'
    allowed_domains = ['indeed.com']
    start_urls = ['https://www.indeed.com/jobs?q=data+scientist&l=New+York%2C+NY&start=']

    def parse(self, response):
        text = response.xpath('//div[@id="searchCount"]/text()').extract_first().replace(",","")
        current_page, total_jobs = map(lambda x: int(x), re.findall('\d+', text))

        all_result_pages = [ self.start_urls[0] + str(start_job) for start_job in range(0,total_jobs,10)]

        for url in all_result_pages[:100]:
            yield Request(url=url, callback=self.parse_result_page)

    def parse_result_page(self, response):
        jobs_on_page = response.xpath("//td[@id='resultsCol']").xpath("./div[@data-tn-component='organicJob']")

        for job in jobs_on_page:
            job_to_save = {}

            location = job.xpath("./span[@class='location']/text()").extract_first().split(",")
            rating_style = job.xpath(".//span/@style").extract_first()
            link_to_job_detail = "https://www.indeed.com" + job.xpath("./h2/a/@href").extract_first()

            job_to_save['title'] = job.xpath("./h2/a/@title").extract_first()
            job_to_save['city'] = location[0].strip()
            job_to_save['region'] = ''.join(re.findall('[a-zA-Z]+', location[1]))
            job_to_save['region_code'] = ''.join(re.findall('\d+', location[1]))
            job_to_save['company'] = ''.join(job.xpath(".//span[@class='company']//text()").extract()).strip()
            job_to_save['how_long_open'] = job.xpath(".//span[@class='date']/text()").extract_first()

            try:
                reviews = job.xpath(".//span[@class='slNoUnderline']/text()").extract_first()
                job_to_save['number_of_reviews'] = int(''.join(re.findall('\d+', reviews)))
                #The rating in the attribute "style" of the class "span" is shown as the number of pixels. The total number of pixels that corresponds to a 5 star review can be found in the parent "span" class and it is equal to 60 pixels.
                job_to_save['rating'] = float(''.join(re.findall('\d+.\d+', rating_style))) * 5 /60
            except:
                job_to_save['number_of_reviews'] = ""
                job_to_save['rating'] = ""

            yield Request(url=link_to_job_detail, meta=job_to_save, callback=self.parse_job_detail_page)


    def parse_job_detail_page(self, response):
       job_to_save = IndeedJobItem()
       job_to_save = dict((k, response.meta.get(k, None)) for k in vars(IndeedJobItem)['fields'].keys())

       summary_raw = ''.join(response.xpath("//span[@class='summary']//text()").extract())
       job_to_save['summary'] = summary_raw.replace('\n','')

       yield job_to_save
