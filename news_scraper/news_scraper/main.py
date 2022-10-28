import os
from multiprocessing import Pool
from itertools import product
import threading

class Spider_nest():
    def _crawl(self, spider_name=None, arguments=None):
        if spider_name:
            os.system('scrapy crawl {0} {1}_{0}.csv'.format(spider_name, arguments))
        return None

    def activating_nest(self, spiders_list, arguments):
        web_threads = []

        for i in range(len(spiders_list)):
            thread = threading.Thread(target=self._crawl, args=(spiders_list[i], arguments[i]))
            web_threads.append(thread)
            web_threads[i].start()

        for i in range(len(spiders_list)-1):
            web_threads[i].join()    

if __name__ == '__main__':
    little_nest = Spider_nest()

    section_to_scrape = input(">>> Introduzca la sección a recolectar\n[+]")
    pages       = input(">>> Introduzca las paginas a mirar\n[+]")

    arguments_elpais   = "-a section={0} -a pages={1} -o ../../data/{0}".format(section_to_scrape, pages)

    arguments = [arguments_elpais]
    spiders   = ['news_bot_elpais']

    little_nest.activating_nest(spiders, arguments)