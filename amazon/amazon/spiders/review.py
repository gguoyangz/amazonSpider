# -*- coding: utf-8 -*-
import scrapy

from amazon.items import ReviewItem

from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait

from scrapy.conf import settings
# scrapy信号库相关
from scrapy import signals
from pydispatch import dispatcher

from selenium import webdriver 
from selenium.common.exceptions import TimeoutException 
from selenium.webdriver.common.by import By 
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC 
from selenium.webdriver.common.keys import Keys 
from scrapy.http import HtmlResponse 
from logging import getLogger 
import time


class ReviewSpider(scrapy.Spider):
    name = 'review'
    allowed_domains = ['www.amazon.com']
    start_urls = ['http://www.amazon.com/']
    detail_url = 'https://www.amazon.com/product-reviews/{asin}/reviewerType=all_reviews'
    review_single_url = 'https://www.amazon.com/product-reviews/{asin}/reviewerType=all_reviews?pageNumber={page}'
    

    asin_list = []  # 商品asin列表
    browser = None # chrome
    reviews_num = 0 # 当前商品的总review数
    pages = 0 # review页码总数
    html = None # review页的整个html
    
    def start_requests(self):
        # 从源文件生成asin对象
        self.load_file()
        # 初始化chrome
        #从settings获取参数
        self.timeout = settings.get('SELENIUM_TIMEOUT')
        self.isLoadingImage = settings.get('LOAD_IMAGE')
        self.windowHeight = settings.get('WINDOW_HEIGHT')
        self.windowWidth = settings.get('WINDOW_WIDTH')

        self.browser = webdriver.Chrome()
        if self.windowHeight and self.windowWidth:
            self.browser.set_window_size(self.windowHeight, self.windowWidth)
        self.browser.set_page_load_timeout(self.timeout)
        self.wait = WebDriverWait(self.browser, 10)
        self.enter_all_reviews()

    # 读取asin文件
    def load_file(self):
        f = open('./asin.txt')
        line = f.readline()
        while line:
            self.asin_list.append(line.strip())
            line = f.readline()
        f.close()

    # 进入all reivews页面
    def enter_all_reviews(self):
        for item in self.asin_list:
            self.browser.get(self.detail_url.format(asin=item))
            
            try:
                span = self.wait.until(
                            EC.presence_of_element_located((By.XPATH, "//*[@id='cm_cr-product_info']/div/div[1]/div[2]/div/div/div[2]/div/span"))
                        )
            finally:
                # 获取评论总数  2,233个 这种去除逗号
                self.reviews_num = int(span.text.replace(',',''))
                pages = int((self.reviews_num / 10) + 1)
                self.enter_single_review(item, pages)
    
    # 进入每页review
    def enter_single_review(self, param_asin, param_pages):
        for i in range(param_pages):
            self.browser.get(self.review_single_url.format(asin=param_asin, page=(i+1)))
            self.crawl_data()
    
    # 抓取每页数据 TODO
    def crawl_data(self):
        self.get_data_obj()
    
    # 生成数据对象
    def get_data_obj(self):
        try:
            self.html = self.wait.until(
                        EC.presence_of_element_located((By.XPATH, "/html"))
                    )
        finally:
            print('333333333333333333333333333333333333333333333333333333333333333333333333')
            print('333333333333333333333333333333333333333333333333333333333333333333333333')
            print('333333333333333333333333333333333333333333333333333333333333333333333333')
            print('333333333333333333333333333333333333333333333333333333333333333333333333')
            # print(self.html)
            # TODO 将selenium获得的html元素转为beautiful的再进行后续操作
            soup = BeautifulSoup(self.html, 'lxml')
            print(soup.prettify())














    # 2.确认搜索结果已经出现后
    def get_search_result(self):
        # 暂时发现存在两种布局的商品搜索结果，由try进行区分

        try:
            product_name_div = self.wait.until(
                        EC.presence_of_element_located((By.XPATH, "//*[@id='search']/div[1]/div[2]/div/span[3]/div[1]/div/div/div/div/div[2]/div[2]/div/div[1]/h2/a/span"))
                    )
        except Exception as e:
            product_name_div = self.wait.until(
                        EC.presence_of_element_located((By.XPATH, "//*[@id='search']/div[1]/div[2]/div/span[3]/div[1]/div/div/div/div/div[2]/div[2]/div/div[1]/div/div/div[1]/h2/a/span"))
                    )
        finally:
            # 点击进入所搜索商品的页面
            product_name_div.click()
            product_name__detail_div = self.browser.findElement(By.xpath("//*[@id=‘acrCustomerReviewText’]"))
            product_name__detail_div.click()
            # try:
            #     product_name__detail_div = self.wait.until(
            #             EC.presence_of_element_located((By.XPATH, "//span[@id='acrCustomerReviewText']"))
            #         )
            # finally:
            #     product_name__detail_div.click()
                # self.enter_all_reviews()
            
            
    

    # 2.2下拉至浏览器最低部
    # def pull_down(self):
    #     self.browser.execute_script("""
    #             window.scrollTo(0,document.body.scrollHeight)
    #             """
    #             )
    #     self.enter_all_reviews()

    # 3.进入所有all review页
    # def enter_all_reviews(self):
    #     all_reviews_btn = self.wait.until(
    #                         EC.presence_of_element_located((By.XPATH, "//*[@id='reviews-medley-footer']/div[2]/a"))
    #                     )
    #     all_reviews_btn.click()
    
    # 4.读取每页review信息
    def take_review(self):
        self.html_selenium = self.browser.execute_script("return document.documentElement.outerHTML") 
        print('5432562436234623462346234562346342')
        time.sleep(10)

    # 关闭chrome方法
    def reviewSpiderCloseHandle(self, spider):
        print('reviewSpider close')
        self.browser.quit()


    def parse(self, response):
        pass

    
