#-*- coding:utf-8 -*-
"""

TODO : https://www.unisq.edu.au/study
"""
import re

import requests
from lxml import etree
from threading import Thread
import pandas as pd

class Spider(object):
    def get_html(self,href):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'
        }
        res = requests.get(href,headers=headers).content.decode()
        html = etree.HTML(res)
        return html

    def get_main(self):
        href = 'https://www.unisq.edu.au/study'
        html = self.get_html(href)
        titles = html.xpath("//div[@class='container']/div[3]/div/a/@title")[:14]
        hrefs = html.xpath("//div[@class='container']/div[3]/div/a/@href")[:14]
        hrefs = ['https://www.unisq.edu.au'+href for href in hrefs]
        for href,title in zip(hrefs,titles):
            html = self.get_html(href)
            divs = html.xpath("//div[@data-gtm-component='discipline-table']/div/div[contains(@class,'row d-md-flex')]")
            th = []
            for div in divs:
                name = div.xpath("./div/a/span/text()")[0]
                link = 'https://www.unisq.edu.au'+div.xpath("./div/a/@href")[0]
                t = Thread(target=self.parse,args=(link,title,name))
                t.start()
                th.append(t)
            [t.join() for t in th]


    def parse(self,link,title,name):
        html = self.get_html(link)
        # 本科
        divs = html.xpath("//div[@data-filter-value='UGRD,ALL']")
        degree = "Undergraduate"
        th = []
        for div in divs:
            href = div.xpath("./a/@href")[0]
            faculty = div.xpath("./a/div/div/text()")[0]
            t = Thread(target=self.get_detail,args=(href,degree,faculty,title,name))
            t.start()
            th.append(t)
        [t.join() for t in th]
        th = []
        divs = html.xpath("//div[@data-filter-value='PGRD,ALL']")
        degree = "Postgraduate"
        for div in divs:
            href = div.xpath("./a/@href")[0]
            faculty = div.xpath("./a/div/div/text()")[0]
            t = Thread(target=self.get_detail, args=(href, degree, faculty, title, name))
            t.start()
            th.append(t)
        [t.join() for t in th]
        th = []
        divs = html.xpath("//div[@data-filter-value='RSCH,ALL']")
        degree = "Research"
        for div in divs:
            href = div.xpath("./a/@href")[0]
            faculty = div.xpath("./a/div/div/text()")[0]
            t = Thread(target=self.get_detail, args=(href, degree, faculty, title, name))
            t.start()
            th.append(t)
        [t.join() for t in th]

    def get_detail(self,href,degree,faculty,title,name):
        list1 = {}
        list1['href'] = href
        list1['study area'] = title
        list1['agriculture and environment'] = name.replace("\r\n",'').strip()
        list1['degree'] = degree
        list1['faculty'] = faculty.replace("\r\n",'').strip()
        html = self.get_html(href)
        list1['ATAR'] = ' '.join([i.strip() for i in html.xpath("//td[text()='ATAR']/following-sibling::td[1]//text()") if i !='']).replace("\r\n",'').strip()
        list1['mode'] = ' '.join([i.strip() for i in html.xpath("//div[contains(@class,'row pb-4 u-equal-height-columns')]/div[2]/ul//text()") if i !='']).replace("\r\n",'').strip()
        list1['location'] = ' '.join([i.strip() for i in html.xpath("//div[contains(@class,'row pb-4 u-equal-height-columns')]/div[4]/ul//text()") if i !='']).replace("\r\n",'').strip()
        list1['duration'] = ' '.join([i.strip() for i in html.xpath("//div[contains(@class,'row pb-4 u-equal-height-columns')]/div[6]/ul//text()") if i !='']).replace("\r\n",'').strip()
        list1['start'] = ' '.join([i.strip() for i in html.xpath("//div[contains(@class,'row pb-4 u-equal-height-columns')]/div[7]/ul//text()") if i !='']).replace("\r\n",'').strip()
        list1['desc'] = ' '.join([i.strip() for i in html.xpath("//div[@id='overview']//text()") if i !='']).replace("\r\n",'').strip().replace('Overview   ','')
        list1['careers'] = ' '.join([i.strip() for i in html.xpath("//div[@id='career-outcomes']//text()") if i !='']).replace("\r\n",'').strip().replace('Career outcomes   ','')
        list1['degree structure'] = ' '.join([i.strip() for i in html.xpath("//div[@id='degree-structure']//text()") if i !='']).replace("\r\n",'').strip().replace('Degree structure  ','')
        list1['domestic_full'] = ' '.join([i.strip() for i in html.xpath("//td[contains(text(),'Domestic full')]/following-sibling::td/text()") if i !='']).replace("\r\n",'').strip().replace("AUD",'')
        href = href + '/international'
        html = self.get_html(href)
        list1['Entry requirements'] = ' '.join(
            [i.strip() for i in html.xpath("//div[@id='entry-requirements']/div[2]/div/div//text()") if
             i != '']).replace("\r\n", '').strip()
        trs = html.xpath("//h2[text()='Fees and scholarships']/../../../../..//tbody/tr")
        for tr in trs:
            list1['international Study Mode'] = re.sub('\s','',''.join(tr.xpath("./td[1]/text()")).replace('/Online',''))
            list1['international Cost'] = ''.join(tr.xpath("./td[2]/text()")).replace('AUD ','')
            datas.append(list1)
        print(list1)

    def save(self,datas):
        df = pd.DataFrame(datas)
        df.to_excel("usq.xlsx",index = False)


if __name__ == '__main__':
    datas = []
    spider = Spider()
    spider.get_main()
    spider.save(datas)
