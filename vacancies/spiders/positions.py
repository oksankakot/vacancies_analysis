import scrapy
from scrapy.http import Response


class PositionsSpider(scrapy.Spider):
    name = "positions"
    allowed_domains = ["www.work.ua"]
    start_urls = ["https://www.work.ua/jobs-python+developer/"]

    def parse(self, response: Response, **kwargs):
        jobs = response.css(".card-search")

        for job in jobs:
            full_title = job.css("h2 a::attr(title)").get()
            title = full_title.split(',')[0] if full_title else 'No information'
            salary_element = job.css("div > span.strong-600")
            salary = salary_element.css("::text").get().strip().replace('\u202f', ' ').replace('\u2009', ' ').replace(
                '\xa0', ' ') if salary_element else 'No information'

            description_link = job.css("h2 a::attr(href)").get()
            if description_link:
                yield response.follow(description_link, callback=self.parse_description, meta={'title': title, 'company': job.css(".add-top-xs .strong-600::text").get(), 'salary': salary})
            else:
                yield {
                    "title": title,
                    "company": job.css(".add-top-xs .strong-600::text").get(),
                    "salary": salary,
                    "description": "No information",
                    "technologies": []  # Добавляем пустой список технологий по умолчанию
                }

        next_page = response.css(".pagination > li")[-1].css("a::attr(href)").get()

        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)

    def parse_description(self, response):
        title = response.meta['title']
        company = response.meta['company']
        salary = response.meta['salary']

        description_element = response.css("#job-description")
        description = ' '.join(description_element.css("::text").getall()).strip() if description_element else 'No information'

        technologies = self.parse_technologies(response)

        yield {
            "title": title,
            "company": company,
            "salary": salary,
            "description": description,
            "technologies": technologies if technologies else []
        }

    def parse_technologies(self, response):
        return response.css(".label-skill .ellipsis::text").getall()
