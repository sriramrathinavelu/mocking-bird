# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class CodercareerItem(scrapy.Item):
	company = scrapy.Field()
	question = scrapy.Field()
	answer = scrapy.Field()
