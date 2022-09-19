#-*- coding:utf-8 -*-
import json
import re
import requests
import pandas as pd
from lxml import etree
from threading import Thread


class Spider(object):
    def __init__(self,url):
        self.url = url
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'
        }

    def get_html(self,url):
        res = requests.get(url,headers = self.headers)
        html = etree.HTML(res.content.decode())
        return html


    def main(self):
        html = self.get_html(self.url)
        divs = html.xpath("//div[@class='tiles__item']")
        for div in divs:
            faculy = div.xpath("./a/div[2]/text()")[0]
            href = div.xpath("./a/@href")[0]
            html = self.get_html(href)
            print(1)
            items = html.xpath("//div[@class='course-accordion__item'][position()<count(//div[@class='course-accordion__item'])]")
            print(len(items))
            for item in items:
                degree = item.xpath("./button/span/text()")[0]
                lis = item.xpath(".//ul/li")
                th = []
                for li in lis:
                    # self.parse(li,faculy,degree)
                    t = Thread(target=self.parse, args=(li, faculy,degree))
                    t.start()
                    th.append(t)
                [t.join() for t in th]



    def parse(self,li,faculy,degree):
        list1 = {}
        list1['faculy'] = faculy
        list1['degree'] = degree
        url = li.xpath("./a/@href")[0]
        if 'www' not in url:
            list1['url'] = 'https://www.une.edu.au' + url
        else:
            list1['url'] = url
        list1['course name'] = li.xpath("./a//text()")[0]
        if list1['course name'] == '':
            list1['course name'] = list1['url'].split("/")[-1].replace("-",'')
        html = self.get_html(list1['url'])
        list1['overview'] = ''.join(html.xpath("//*[@id='key-facts']/../following-sibling::div[1]//text()")).strip()
        if list1['overview'] == '':
            list1['overview'] = ''.join(html.xpath("//div[@class='fact-listing__item fact-listing__item--entry-requirements']/div[@data-audience='domestic']/p//text()")).strip()
        list1['Duration'] = ';'.join(html.xpath("//*[text()='Duration']/../following-sibling::ul//text()")).strip()
        list1['Mode'] = ';'.join(html.xpath("//*[text()='Mode']/../following-sibling::ul//text()")).strip()
        list1['Campus'] = ';'.join(html.xpath("//*[text()='Campus']/../following-sibling::ul//text()")).strip()
        list1['ATAR'] = ';'.join(
            html.xpath("//*[text()='Entry requirements']/../following-sibling::ul//text()")).strip().split(":")[1]
        list1['career options'] = ' '.join(html.xpath("//*[text()='Career outcomes']/following-sibling::div//text()")).strip()
        list1['Entry requirements'] = ''.join(
            html.xpath("//*[text()='Entry requirements']/following-sibling::p//text()")).strip()
        list1['international fee'] = ''.join(
            html.xpath("//td[text()='International']/following-sibling::td/text()")).replace('*', '').replace('$',
                                                                                                              '').replace(
            ',', '').strip()
        list1['domestic fee'] = ''.join(
            html.xpath("//td[text()='Commonwealth Supported Place']/following-sibling::td/text()")).replace('*',
                                                                                                            '').replace(
            '$', '').replace(',', '').strip()
        print(list1)
        print("*" * 50)
        datas.append(list1)


    def save(self):
        df = pd.DataFrame(datas)
        df.to_excel("une.xlsx",index = False)


if __name__ == '__main__':
    datas = []
    url = 'https://www.une.edu.au/study'
    spider = Spider(url)
    spider.main()
    spider.save()
