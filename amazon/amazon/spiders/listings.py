# -*- coding: utf-8 -*-
import scrapy
from scrapy import Spider, Request
from amazon.items import ListingItem

from bs4 import BeautifulSoup
import re

class ListingsSpider(scrapy.Spider):
    name = 'listings'
    allowed_domains = ['www.amazon.com']
    start_urls = ['http://www.amazon.com/']

    detail_url = 'https://www.amazon.com/dp/{asin}'
    asin_list = [] # asin码列表

    # 局部设置时间间隔
    custom_settings = {
        'DOWNLOAD_DELAY': 3,
        "RANDOM_MIN_DELAY": 0,
        "RANDOM_MAX_DELAY": 3
    }

    def start_requests(self):
        self.asin_list = self.load_file()
        for asin in self.asin_list:
            yield Request(self.detail_url.format(asin=asin),meta={'asin': asin}, callback=self.parse_index)

    # 爬取页面数据
    def parse_index(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        item = ListingItem()
        # 1.表格信息内容(asin、dimension、item_weight、ship_weight、bsr)
        # 1.1 合并左右两表格信息
        table_dic = {**self.table_left_obj(soup), **self.table_right_obj(soup)}
        if 'ASIN' in table_dic:
            item['asin'] = table_dic['ASIN'] or ''
        else:
            item['asin'] = ''
        if 'Product Dimensions' in table_dic:
            item['dimension'] = table_dic['Product Dimensions'] or ''
        elif 'Package Dimensions' in table_dic:
            item['dimension'] = table_dic['Package Dimensions'] or ''
        else:
            item['dimension'] = ''
        if 'Item Weight' in table_dic:
            item['item_weight'] = table_dic['Item Weight'] or ''
        else:
            item['item_weight'] = ''
        if 'Shipping Weight' in table_dic:
            item['ship_weight'] = table_dic['Shipping Weight'] or ''
        else:
            item['ship_weight'] = ''
        if 'Date first listed on Amazon' in table_dic:
            item['first_date'] = table_dic['Date first listed on Amazon'] or ''
        elif 'Date First Available' in table_dic:
            item['first_date'] = table_dic['Date First Available'] or ''
        else:
            item['first_date'] = ''
        if 'Best Sellers Rank' in table_dic:
            item['bsr'] = table_dic['Best Sellers Rank'] or ''
        else:
            item['bsr'] = ''
        
        # 2.抓取品类和品类入口
        if soup.find('div', id='wayfinding-breadcrumbs_feature_div') != None:
            category_path = soup.find('div', id='wayfinding-breadcrumbs_feature_div').get_text()
            item['category_path'] = category_path.strip().replace('\n', '').replace(' ', '')
            cate_div_first_index =  category_path.find('›')
            if cate_div_first_index != -1:
                item['category'] = category_path[0:cate_div_first_index].strip()
        # 品牌、名称、链接、当前售价、星级、amazon's choice、评论数、配送方式
        if soup.find('a', id='bylineInfo').get_text() != None:
            item['brand'] = soup.find('a', id='bylineInfo').get_text() or ''
        else:
            item['brand'] = ''
        if soup.find('span', id='productTitle') != None:
            item['pro_name'] = soup.find('span', id='productTitle').get_text().strip() or ''
        else:
            item['pro_name'] = ''
        item['pro_url'] = self.detail_url.format(asin=response.meta['asin']) or ''
        if soup.find('span', id='priceblock_ourprice') != None:
            item['price'] = soup.find('span', id='priceblock_ourprice').get_text() or ''
        else:
            item['price'] = ''
        if soup.find('span', id='acrPopover').get('title')[0:3] != None:
            item['star'] = soup.find('span', id='acrPopover').get('title')[0:3] # 获得title值后取前3位
        else:
            item['star'] = ''
        if soup.find('span', class_='a-size-small aok-float-left ac-badge-rectangle') != -1:
            item['amazon_c'] = 'yes'
        else:
            item['zmazon_c'] = 'no'
        # 评论数
        if soup.find('span', id='acrCustomerReviewText') != None:
            temp_review = soup.find('span', id='acrCustomerReviewText').get_text().replace(',', '')
            temp_review = temp_review[0:temp_review.index(' ')]
            item['review_num'] = int(temp_review) or ''
        else:
            item['review_num'] = ''
        # 配送方式当id为merchant-info不是所需div时，用usedbuyBox来识别
        if soup.find('div', id='merchant-info') != None:
            item['delivery'] = soup.find('div', id='merchant-info').get_text().strip()
        if item['delivery'] == '':
            if soup.find('div', id='usedbuyBox') != None:
                if soup.find('div', id='usedbuyBox').find('div', class_='a-section a-spacing-base') != None:
                    temp_delev = soup.find('div', id='usedbuyBox').find('div', class_='a-section a-spacing-base').get_text().strip().replace('\n', '')
                    temp_delev = ' '.join(temp_delev.split())
                    if temp_delev.find('Sold') != -1:
                        temp_delev_index = temp_delev.index('Sold')
                        item['delivery'] = temp_delev[temp_delev_index:]
        # 爬取图片url
        if soup.find('img', id='landingImage')['data-a-dynamic-image'] != None:
            imgs_dict = eval(soup.find('img', id='landingImage')['data-a-dynamic-image'])
            imgs_url = []
            for key in imgs_dict:
                imgs_url.append(key)
            item['image_url'] = ";".join(imgs_url)
        # 产品特点
        if soup.find('ul', class_='a-unordered-list a-vertical a-spacing-none') != None:
            if soup.find('ul', class_='a-unordered-list a-vertical a-spacing-none').findAll('span', class_='a-list-item') != None:
                feature_list_ele = soup.find('ul', class_='a-unordered-list a-vertical a-spacing-none').findAll('span', class_='a-list-item')
                feature_list = []
                for feature_item in feature_list_ele:
                    feature_list.append(feature_item.get_text().strip().replace('\t', '').replace('\n', ''))
                if feature_list[0] == 'Make sure this fitsby entering your model number.':
                    del feature_list[0]
                item['featrue'] = "\n".join(feature_list)
        yield item

    # 生成table数据对象
    def table_left_obj(self, soup_obj):
        table = soup_obj.find('table', id='productDetails_techSpec_section_1')
        table_ths = table.findAll('th', class_='a-color-secondary a-size-base prodDetSectionEntry')
        table_tds = table.findAll('td')
        # key值k_list,val值v_list
        k_list = []
        v_list = []
        for i in table_ths:
            k_list.append(i.get_text().strip())
        for i in table_tds:
            v_list.append(i.get_text().strip())
        # 生成表格对应的kv对象
        obj = {}
        for i in range(len(table_ths)):
            obj[k_list[i]] = v_list[i]
        # 针对bsr进行格式优化，去除bsr中的换行符，去除点击文字
        obj = self.bsr_ship_weight_format(obj)
        return obj
    
    # 生成右侧表格对象
    def table_right_obj(self, soup_obj):
        table = soup_obj.find('table', id='productDetails_detailBullets_sections1')
        table_ths = table.findAll('th', class_='a-color-secondary a-size-base prodDetSectionEntry')
        table_tds = table.findAll('td')
        # key值k_list,val值v_list
        k_list = []
        v_list = []
        for i in table_ths:
            k_list.append(i.get_text().strip())
        for i in table_tds:
            v_list.append(i.get_text().strip())
        # 生成表格对应的kv对象
        obj = {}
        for i in range(len(table_ths)):
            obj[k_list[i]] = v_list[i]
        # 针对bsr进行格式优化，去除bsr中的换行符，去除点击文字
        obj = self.bsr_ship_weight_format(obj)
        return obj

    # 1.bsr有()号则去除 2.ship weight格式去除后面括号内容
    def bsr_ship_weight_format(self, param_obj):
        if 'Best Sellers Rank' in param_obj:
            # 针对不同商品bsr，有()号则去除
            if param_obj['Best Sellers Rank'].find('(') != -1:
                left_index = param_obj['Best Sellers Rank'].index('(')
                right_index = param_obj['Best Sellers Rank'].index(')')
                param_obj['Best Sellers Rank'] = ((param_obj['Best Sellers Rank'][0:left_index] + param_obj['Best Sellers Rank'][right_index+1:])).replace('\n', ' ')
                param_obj['Best Sellers Rank'] = param_obj['Best Sellers Rank'].strip()
        if 'Shipping Weight' in param_obj:
            if param_obj['Shipping Weight'].find('(') != -1:
                left_index = param_obj['Shipping Weight'].index('(')
                param_obj['Shipping Weight'] = param_obj['Shipping Weight'][0:left_index]
        return param_obj

    def parse(self, response):
        pass

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