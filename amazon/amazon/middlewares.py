# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy.conf import settings
from scrapy.downloadermiddlewares.useragent import UserAgentMiddleware
from scrapy.downloadermiddlewares.httpproxy import HttpProxyMiddleware
import random

from scrapy import signals

from selenium import webdriver 
from selenium.common.exceptions import TimeoutException 
from selenium.webdriver.common.by import By 
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC 
from selenium.webdriver.common.keys import Keys 
from scrapy.http import HtmlResponse 
from logging import getLogger 
import time

from amazon.settings import IPPOOL


class AmazonSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Response, dict
        # or Item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class AmazonDownloaderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)

# 随机userAgent代理
class MyUserAgentMiddleware(UserAgentMiddleware):
    def __init__(self, user_agent):
        self.user_agent = user_agent

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            user_agent=crawler.settings.get('MY_USER_AGENT')
        )

    def process_request(self, request, spider):
        agent = random.choice(self.user_agent)
        request.headers['User-Agent'] = agent

# IP代理池
# IP代理池
class IPPOOLS(HttpProxyMiddleware):
    def __init__(self, ip=""):
        self.ip = ip

    def process_request(self, request, spider):
        thisip = random.choice(IPPOOL)
        print("当前使用的IP为： " + thisip["ipaddr"])
        request.meta["proxy"] = "http://" + thisip["ipaddr"]


# selenium测试中间件
class SeleniumMiddleware():
    def process_request(self, request, spider):
        print(f'chrome is getting page')
        useSelenium = request.meta.get('useSelenium', False)
        if useSelenium:
            try:
                spider.browser.get(request.url)
                # 等待搜索框
                input = spider.wait.until(
                    EC.presence_of_element_located((By.XPATH, "//input[@id='twotabsearchtextbox']"))
                )
                time.sleep(2)
                input.clear()
                input.send_keys('B07Q77JLXX') # 测试商品asin
                input.send_keys(Keys.RETURN)
                # 等待搜索结果
                searchRes = spider.wait.until(
                    EC.presence_of_element_located((By.XPATH, ".//span[contains(@class,'s-include-content-margin')]"))
                )
            except Exception as e:
                print(f"chrome getting apge error, Exception={e}")
                return HtmlResponse(url=request.url, status=500, request=request)
            else:
                time.sleep(3)
                # 页面爬取成功返回页面元素对象
                return HtmlResponse(
                    url = request.url,
                    body = spider.browser.page_source,
                    request = request,
                    # 暂时采用utf-8对返回对象进行编码
                    encoding = 'utf-8',
                    status = 200
                )
