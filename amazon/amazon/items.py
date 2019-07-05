# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class AmazonItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

# reviews数据
class ReviewItem(scrapy.Item):
    # 产品名、Asin、用户名、星级、标题、日期、内容、有用数
    pro_name = scrapy.Field()
    asin = scrapy.Field()
    name = scrapy.Field()
    star = scrapy.Field()
    title = scrapy.Field()
    date = scrapy.Field()
    content = scrapy.Field()
    help_num = scrapy.Field()

# listing数据
class ListingItem(scrapy.Item):
    # asin、商品名、品类、品类入口、地址链接、品牌、当前售价、星级、amazon'choice、revie数、配送方式、图片链接、特点、produc dimensions、item weight、ship item、first_date、bsr
    asin = scrapy.Field()
    pro_name = scrapy.Field()
    category = scrapy.Field()
    category_path = scrapy.Field()
    pro_url = scrapy.Field()
    brand = scrapy.Field()
    price = scrapy.Field()
    star = scrapy.Field()
    amazon_c = scrapy.Field()
    review_num = scrapy.Field()
    delivery = scrapy.Field()
    image_url = scrapy.Field()
    featrue = scrapy.Field()
    dimension = scrapy.Field()
    item_weight = scrapy.Field()
    ship_weight = scrapy.Field()
    first_date = scrapy.Field()
    bsr = scrapy.Field()

