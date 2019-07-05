# -*- coding: utf-8 -*-
import scrapy
from scrapy import Spider, Request
from amazon.items import ReviewItem

from bs4 import BeautifulSoup
import re

class ReviewsSpider(scrapy.Spider):
    name = 'reviews'
    allowed_domains = ['www.amazon.com']
    start_urls = ['http://www.amazon.com/']

    detail_url = 'https://www.amazon.com/product-reviews/{asin}/reviewerType=all_reviews'
    review_single_url = 'https://www.amazon.com/product-reviews/{asin}/reviewerType=all_reviews?pageNumber={page}'

    asin_list = []  # 商品asin列表

    # 局部设置时间间隔
    custom_settings = {
        'DOWNLOAD_DELAY': 2, # 2秒抓取10条review
        "RANDOM_MIN_DELAY": 0,
        "RANDOM_MAX_DELAY": 3
    }
    reviews_nums = 0 # review总数

    def start_requests(self):
        self.asin_list = self.load_file()
        for item in self.asin_list:
            # 进入某个asin商品review页
            yield Request(self.detail_url.format(asin=item),meta={'asin': item}, callback=self.parse_asin_index)

        
    def parse_asin_index(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        # 获取商品名称
        product_name = soup.find(
            'h1', class_='a-size-large a-text-ellipsis').get_text()
        # 获取review总数
        reviews_num = soup.find(
            'span', class_='a-size-medium totalReviewCount'
        ).get_text()
        # 将类似2,220数量转为2220
        reviews_num = int(reviews_num.replace(',', ''))

        self.reviews_nums += self.reviews_nums + int(reviews_num)
        print('----------------------------------------------')
        print('----------------------------------------------')
        print('检索到asin编码为{asin}的商品有{num}条review,所有商品总review累计共有{all_num}'.format(asin=response.meta['asin'], num=reviews_num, all_num=self.reviews_nums))
        print('----------------------------------------------')
        print('----------------------------------------------')
        page_num = int(int(reviews_num) / 10 + 1)
        for i in range(page_num):
            yield Request(self.review_single_url.format(asin=response.meta['asin'], page=(i+1)), meta={'pro_name': product_name, 'asin': response.meta['asin']}, callback=self.parse_detail)
    
    def parse_detail(self, response):
        # 爬取每页数据
        soup = BeautifulSoup(response.text, 'lxml')
        review_List = soup.find_all(
            'div', class_='a-section celwidget'
        )
        for review in review_List:
            item = ReviewItem()
            item['pro_name'] = response.meta['pro_name']
            item['asin'] = response.meta['asin']
            item['name'] = review.find(
                'span', class_='a-profile-name'
            ).get_text() or ''
            item['title'] = review.find(
                'a', class_='a-size-base a-link-normal review-title a-color-base review-title-content a-text-bold'
            ).find('span').get_text() or ''
            item['star'] = self.extract_first_number(review.find(
                'span', class_='a-icon-alt'
            ).get_text()) or 0
            item['date'] = review.find(
                'span', class_='a-size-base a-color-secondary review-date'
            ).get_text() or ''
            item['content'] = review.find(
                'span', class_='a-size-base review-text review-text-content'
            ).find('span').get_text() or ''
            # 当没有已帮助数时则为0
            if review.find('span', class_='a-size-base a-color-tertiary cr-vote-text') != None:
                help_num_temp = self.extract_number(review.find(
                                    'span', class_='a-size-base a-color-tertiary cr-vote-text'
                                ).get_text())
                help_num_temp = self.extract_number(help_num_temp)
                item['help_num'] = help_num_temp
                # item['help_num'] = self.extract_number(review.find(
                #     'span', class_='a-size-base a-color-tertiary cr-vote-text'
                # ).get_text()) or 0
            else:
                 item['help_num'] = self.extract_number('0')
            yield item


    # 读取asin文件
    def load_file(self):
        lists = []
        f = open('./asin.txt')
        line = f.readline()
        while line:
            lists.append(line.strip())
            line = f.readline()
        f.close()
        return lists

    # 针对帮助数：提取字符串中的数字
    def extract_number(self, param_str):
        param_str = str(param_str)
        if re.findall(r"\d+\.?\d*",param_str) != []:
            return re.findall(r"\d+\.?\d*",param_str)[0]
        return 1
    
    # 针对星级：提取字符串第一个字符
    def extract_first_number(self, param_str):
        param_str = str(param_str)
        return param_str[0]

    def parse(self, response):
        pass
