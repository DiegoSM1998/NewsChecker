# -*- coding: utf-8 -*-
import scrapy
import re
import requests
import datetime

from bs4 import BeautifulSoup as soup
from urllib.request import urlopen

from news_scraper.items import NewsItem


class newsSpider_bot_elpais(scrapy.Spider):
    name = 'news_bot_elpais'

    def __init__(self, section=None, pages=1,*args, **kwargs):
        self.start_urls             = ['https://elpais.com/{}/'.format(section)]
        self.pattern_auto_ads       = re.compile(".google")
        self.pattern_patron_ads     = re.compile(".outbrain")
        self.pattern_sources        = re.compile(".apunta [a-zA-ZñÑáéíóúÁÉÍÓÚ ]*[,]* " +
                                                    "|.señala [a-zA-ZñÑáéíóúÁÉÍÓÚ ]*[,]* " +
                                                    "|.dice [a-zA-ZñÑáéíóúÁÉÍÓÚ ]*[,]* " +
                                                    "|.añade [a-zA-ZñÑáéíóúÁÉÍÓÚ ]*[,]* " +
                                                    "|.fuentes [a-zA-ZñÑáéíóúÁÉÍÓÚ ]*[,]* " +
                                                    "|.ha dicho [a-zA-ZñÑáéíóúÁÉÍÓÚ ]*[,]* "
                                                    "|.según [a-zA-ZñÑáéíóúÁÉÍÓÚ ]*[,]* "
                                                    "|.opina [a-zA-ZñÑáéíóúÁÉÍÓÚ ]*[,]* "
                                                    "|, [a-zA-ZñÑáéíóúÁÉÍÓÚ ]* ,", re.I)
        self.pattern_bad_words      = re.compile(" [']*feminazi[']* | [']*progre[']* | [']*facha[']* | [']*zorra[']* | [']*puta[']* | [']*puto[']* " +
                                                    "| [']*gilipollas[']* | [']*mierda[']* | [']*tetas[']* | [']*gilipollas[']* " +
                                                    "| [']*podemita[']* | [']*caca[']* | [']*culo[']* | [']*pedo[']* | [']*follar[']* | [']*travelo[']* " +
                                                    "| [']*maricon[']* | [']*marica[']* | [']*bollera[']* | [']*tortillera[']* | [']*catalufos[']* " +
                                                    "| [']*perroflauta[']* | [']*sudaca[']* | [']*guachupino[']* | [']*tiraflechas[']* | [']*moro[']* ")

        super(newsSpider_bot_elpais, self).__init__(*args, **kwargs)

    def parse(self, response):

        for src in response.xpath("//figure[contains(@class, 'foto  foto_w1200')]/a/@href"):
            url = src.extract()
            yield scrapy.Request(url, callback=self.parse_dir_contents)
    
    def parse_dir_contents(self, response):
        item                        = NewsItem()
        counter_autogenerate_ads    = 0
        counter_patron_ads          = 0
        text                        = ""

        item['title']           = response.xpath("//h1[contains(@class, 'articulo-titulo')]/text()").extract()
        item['subtitle']        = response.xpath("//h2[contains(@class, 'articulo-subtitulo')]/text()").extract()
        
        for paragraph in response.xpath("//p/text()").extract():
            text += paragraph

        item['text']            = text     
        item['author']          = response.xpath("//span[contains(@class, 'autor-nombre')]/a/text()").extract()

        item['url']             = response.xpath("//meta[@property='og:url']/@content").extract()
        news_datetime           = response.xpath("//time/@datetime").extract()
        news_datetime = news_datetime[0].split("T")
        
        item['upload_hour'] = news_datetime[1]
        item['upload_date'] = news_datetime[0]
        
        # contains(@href, 'addClick') or 
        # [contains(@src, 'googlesyndication')]

        ads_autogenerate_scripts    = response.xpath("//script").extract()
        internal_html               = response.xpath("//html").extract()

        counter_autogenerate_ads    = len(internal_html) - 1

        for script in ads_autogenerate_scripts:
            if self.pattern_auto_ads.search(script) != None:
                counter_autogenerate_ads += 1 

            if self.pattern_patron_ads.search(script) != None:
                counter_patron_ads += 1 

        ratio_ads = counter_autogenerate_ads-counter_patron_ads
        if ratio_ads > 0:
            item['advertising_ratio'] = 1/ratio_ads
        else:
            item['advertising_ratio'] = 0

        coincidences = self.pattern_sources.findall(text)

        item['source'] = ""

        for coincidence in coincidences:
            aux = coincidence.split(" ")

            if aux[len(aux)-2][0].isupper():
                item['source'] += aux[len(aux)-3] + " " + aux[len(aux)-2][:len(aux[len(aux)-2])-1] + ";"

        bad_language = self.pattern_bad_words.findall(text)

        if len(bad_language) > 0:
            item['bad_language'] = 1 
        else:
            item['bad_language'] = 0

        yield item

    def scrape_news(self, number_pages):
        n_pages = int(number_pages)
        

