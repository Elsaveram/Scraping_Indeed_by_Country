# -*- coding: utf-8 -*-
from scrapy import Spider, Request
import re
import urllib
from indeed.items import IndeedJobItem

class IndeedSpider(Spider):
    name = 'indeed_spider'
    start_urls = ["https://www.indeed.com/worldwide"]

    # Filters used are full time jobs opened in the last 30 days within 25 miles (default)
    base_query_params = { 'q':'data scientist', 'fromage':'30' }
    job_levels = ['entry_level', 'mid_level', 'senior_level']

    # The first pass at parsing is grabbing every country indeed has listing in.
    def parse(self, response):
        country_urls = list(set(response.xpath("//tr[@class='countries']//a/@href").extract()))

        for country_url in country_urls:
            country = ''.join(response.xpath("//tr[@class='countries']//a[@href='"+country_url+"']/text()").extract())
            for job_level in self.job_levels:
                url = country_url+r'jobs?'+urllib.parse.urlencode({ **self.base_query_params, **{'explvl':job_level}})
                yield Request(url, meta={'country':country}, callback=self.parse_pages)

    # Find the total number of pages in the result so that we can decide how many urls to scrape next
    def parse_pages(self, response):
        # First we try the US style with two numbers then the international style with three.
        all_result_pages = []

        try:
            page_and_item_count = response.xpath('//div[@id="searchCount"]/text()').extract_first().replace(",","")
            current_page, total_jobs = map(lambda x: int(x), re.findall('\d+', page_and_item_count ))
        except:
            try:
                _, current_page, total_jobs = map(lambda x: int(x), re.findall('\d+', page_and_item_count ))
            except:
                return

        if total_jobs > 999:
            # Break jobs down by location
            locations = response.xpath('//div[@id="LOCATION_rbo"]//li')
            for location in locations:
                location_link = location.xpath('.//@href').extract_first()
                location_name = location.xpath('.//a/text()').extract_first()
                location_url = response.request.url.replace('/jobs', location_link)
                # TBD: Pass location_name in as meta?
                yield Request(url=location_url , meta={'country':response.meta['country']}, callback=self.parse_pages)
        else:
            all_result_pages = [response.request.url+'&start='+str(start_job) for start_job in range(0,total_jobs+10,10)]

        # Yield the requests to different search result urls, using parse_result_page function
        # to parse the response.
        for url in all_result_pages:
            yield Request(url=url, meta={'country':response.meta['country']}, callback=self.parse_result_page)


    def parse_result_page(self, response):
        # Parse the jobs in each page
        jobs_on_page = response.xpath("//td[@id='resultsCol']").xpath("./div[@data-tn-component='organicJob']")

        for job in jobs_on_page:
            # Initiating an empty dictionary to collect the meta information to "piggy-back" forward
            job_to_save = {}

            # Location. It includes the city and some times the state and zip code
            job_to_save['country'] = response.meta['country']
            location = job.xpath("./span[@class='location']/text()").extract_first().split(",")
            job_to_save['city'] = location[0].strip()
            try:
                job_to_save['region'] = ''.join(re.findall('[a-zA-Z]+', location[1]))
                job_to_save['region_code'] = ''.join(re.findall('\d+', location[1]))
            except:
                job_to_save['region'] = ''
                job_to_save['region_code'] = ''

            # Company rating. The rating in the attribute "style" of the class "span" is shown as the number of pixels.
            # The total number of pixels that corresponds to a 5 star review can be found in the parent "span" class
            # and it is equal to 60 pixels.
            rating_style = job.xpath(".//span/@style").extract_first()
            try:
                job_to_save['rating'] = float(''.join(re.findall('\d+.\d+', rating_style))) * 5 / 60
            except:
                job_to_save['rating'] = ""

            # Title, company, how long ago the position was open.
            job_to_save['indeed_id'] = job.xpath("./@data-jk").extract_first()
            job_to_save['title'] = job.xpath("./h2/a/@title").extract_first()
            job_to_save['company'] = ''.join(job.xpath(".//span[@class='company']//text()").extract()).strip()
            job_to_save['how_long_open'] = job.xpath(".//span[@class='date']/text()").extract_first()

            # Salary data does not always exist
            try:
                job_to_save['salary'] = job.xpath(".//td/div/span[@class='no-wrap']/text()").extract_first().strip()
            except:
                job_to_save['salary'] = ""

            # Number of company reviews can be empty so it's wraped it in a try block
            try:
                reviews = job.xpath(".//span[@class='slNoUnderline']/text()").extract_first()
                job_to_save['number_of_reviews'] = int(''.join(re.findall('\d+', reviews)))
            except:
                job_to_save['number_of_reviews'] = 0

            # The job details link is a relative link. Concatenate with start url
            link_to_job_detail = "https://www.indeed.com" + job.xpath("./h2/a/@href").extract_first()

            # Pass the meta information to the job detail page where the summary is going to be extracted
            yield Request(url=link_to_job_detail, meta=job_to_save, callback=self.parse_job_detail_page)


    def parse_job_detail_page(self, response):
        job_to_save = IndeedJobItem()
        indeed_keys = vars(IndeedJobItem)['fields'].keys()
        meta_keys = response.meta.keys()

        # In order to remove unwanted columns from the meta object, we create a dictonary by using the intersecton of
        # the indeed class keys and the meta keys
        job_to_save = dict((k, response.meta[k]) for k in indeed_keys & meta_keys )

        # Add a striped version of the summary
        summary_raw = ''.join(response.xpath("//span[@class='summary']//text()").extract())
        job_to_save['summary'] = summary_raw.replace('\n','')

        yield job_to_save
