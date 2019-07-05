# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import codecs
import json
from openpyxl import Workbook

class AmazonPipeline(object):
    def process_item(self, item, spider):
        return item

class reviewPipeline(object):

    def __init__(self):
        self.wb = Workbook()
        self.ws = self.wb.active
        self.ws.append([
            'Asin', '产品名', '用户名', '星级', '标题', '日期', '内容', '帮助数'
        ])
    
    def process_item(self, item, spider):
        line = [item['asin'], item['pro_name'], item['name'], item['star'], item['title'], item['date'], item['content'], item['help_num']]
        self.ws.append(line)
        self.wb.save('reviews.xlsx')
        return item

class listingPipeline(object):
    def __init__(self):
        self.wb = Workbook()
        self.ws = self.wb.active
        self.ws.append([
            'ASIN', '商品名称', '品类', '类目入口', '链接', '品牌', '当前售价', '评分', 'amazonChoice', 'review数', '配送方式', '图片', '特点', '规格', '商品重量', '运输重量', '首次上架时间', 'BSR'
        ])
    
    def process_item(self, item, spider):
        line = [item['asin'], item['pro_name'], item['category'], item['category_path'], item['pro_url'], item['brand'], item['price'], item['star'], item['amazon_c'], item['review_num'], item['delivery'], item['image_url'], item['featrue'], item['dimension'], item['item_weight'], item['ship_weight'], item['first_date'], item['bsr']]
        self.ws.append(line)
        self.wb.save('listing.xlsx')
        return item
