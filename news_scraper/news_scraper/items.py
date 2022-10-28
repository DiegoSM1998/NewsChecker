# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class NewsItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    title               = scrapy.Field()
    text                = scrapy.Field()
    url                 = scrapy.Field()
    author              = scrapy.Field()
    subtitle            = scrapy.Field()
    upload_hour         = scrapy.Field()
    upload_date         = scrapy.Field()
    source              = scrapy.Field()
    advertising_ratio   = scrapy.Field()
    bad_language        = scrapy.Field()


