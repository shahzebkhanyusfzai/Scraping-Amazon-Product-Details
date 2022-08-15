import scraper_helper
import scrapy, os, re, json
from scrapy.crawler import CrawlerProcess


class amazon(scrapy.Spider):

    name = 'amazon'

    def start_requests(self):
        yield scrapy.Request(url='https://www.amazon.com/s?rh=n%3A165796011&fs=true&ref=lp_165796011_sar')
        
    def parse(self, response):
        links = response.xpath('//a[@class="a-link-normal s-underline-text s-underline-link-text s-link-style a-text-normal"]/@href').getall()
        print(links)
        for link in links:
            link = 'https://www.amazon.com' + link
            yield scrapy.Request(url=link, callback=self.parse_item)
            
        print('----------------')
        nexpage = response.xpath('(//span[@class="s-pagination-strip"]/a)[last()]/@href').get()
        print(nexpage)
        nexpage = 'https://www.amazon.com'+nexpage
        print(nexpage)
        if nexpage:
            yield scrapy.Request(url=nexpage, callback=self.parse)
    
    def parse_item(self,response):
        name = response.xpath('//span[@id="productTitle"]/text()').get()
        # //span[@id="productTitle"]/text()
        print("////////////"+name+'////////////')
        name = scraper_helper.cleanup(name)
        print("////////////"+name+'////////////')
        price = response.xpath('//span[@class="a-price-whole"]/text()').get()
        desc = response.xpath('//div[@id="feature-bullets"]/ul/li/span/text()').getall()
        print(desc)
        desc = ''.join(desc)
        print(desc)
        desc = scraper_helper.cleanup(desc)
        print(desc)
        asin = response.xpath('//th[contains(text(),"ASIN")]/following-sibling::td[1]/text() | //span[contains(text(),"ASIN")]/following-sibling::span/text()').get()
        ranking = response.xpath('//ul[@class="a-unordered-list a-nostyle a-vertical zg_hrsr"]/li/span[@class="a-list-item"]/text()  | //ul[@class="a-unordered-list a-nostyle a-vertical zg_hrsr"]/li/span[@class="a-list-item"]/a/text()').getall()
        ranking = ''.join(ranking)

        images = response.xpath('//div[@id="imgTagWrapperId"]/img/@data-old-hires').get()
        image_name = f'{asin}.jpg'

        seller = response.xpath('//span[contains(text(),"Brand")]/following::td[1]/span/text()').get()
        # categories = response.xpath('//div[@id="wayfinding-breadcrumbs_feature_div"]/ul/li/span/a/text()').get()
        # print(categories)
        # categories = '>'.join(categories)
        # print(categories)
        # categories = scraper_helper.cleanup(categories)


        yield {
            'url': response.url,
            'name': name,
            'price': price,
            'desc': desc,
            # 'categories': categories,
            'asin': asin,
            'ranking': ranking,
            'image': images,
            'image_name': image_name,
            'seller': seller,
            # 'fulfilment': ''
        }
        

filename = 'Sample.csv'
process = CrawlerProcess(settings={
    "FEEDS": {
        filename: {"format": "csv"},
    },
    "CONCURRENT_REQUESTS": 4,
    "DOWNLOAD_DELAY": 0.5,
    "DEFAULT_REQUEST_HEADERS": {
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36'
    },
})

process.crawl(amazon)
process.start()