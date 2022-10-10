#-*- coding:utf-8 -*-
"""
create of author:WV
----------
create of datetime:2022/8/11 14:59
----------
create of software: PyCharm
----------
TODO : https://www.acu.edu.au/study-at-acu/find-a-course
"""
import threading
from urllib.parse import urljoin
import requests
import re
import pandas as pd
from lxml import etree



class Spider(object):
    def __init__(self,url):
        self.url = url
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'
        }

    def get_html(self,url):
        for _ in range(5):
            try:
                res = requests.get(url,headers = self.headers)
                if res.status_code == 200:
                    return etree.HTML(res.content.decode())
            except Exception as e:
                print('Error------',e)
        else:return


    def main(self):
        html = self.get_html(self.url)
        lis = html.xpath("//ul[@id='main-nav']/li[1]/div/div/div[1]/ul/li")
        for li in lis:
            Faculty = li.xpath("./a/text()")[0].strip()
            href = urljoin(url,li.xpath("./a/@href")[0])
            html = self.get_html(href)
            divs = html.xpath("//div[@class='accordion_container']/div")
            for div in divs:
                Degrees = div.xpath("./a/text()")[0].strip()
                courses = div.xpath("./div/ul/li")
                th = []
                for course in courses:
                    t = threading.Thread(target=self.main1,args=(Faculty,Degrees,course))
                    t.start()
                    th.append(t)
                [t.join() for t in th]


    def main1(self,Faculty,Degrees,course):
        list1 = {}
        list1['Faculty'] = Faculty
        list1['Degrees'] = Degrees
        list1['Course_name'] = ''.join(course.xpath("./a/span[2]/text()")).strip()
        list1['href'] = ''.join(course.xpath("./a/@href")).strip()
        html = self.get_html(list1['href'])
        list1['Desc'] = ''.join(html.xpath("//div[@class='col-sm-12']/div/div[2]/div/div/div/div[2]//div[@id]/p//text()")).strip()
        list1['Duration'] = ' '.join([i.strip() for i in html.xpath("/html/body/div[2]/section/div/section[3]/div/div/div[2]/div/div/div[1]/div/div[2]/div/div[1]/div/div[3]/div/p/text()")]).strip()
        list1['Location'] = ' '.join([i.strip() for i in html.xpath("/html/body/div[2]/section/div/section[3]/div/div/div[2]/div/div/div[1]/div/div[2]/div/div[1]/div/div[2]/div/div[2]/ul/li/text()")]).strip().replace('– ','')
        list1['Mode'] = 'Online'
        list1['Domestic_full'] = ' '.join([i.strip() for i in html.xpath("/html/body/div[2]/section/div/section[3]/div/div/div[2]/div/div/div[1]/div/div[2]/div/div[2]/div/div[1]/div/div[2]/ul/li/text()")]).strip().split(": $")[-1]
        list1['International_full'] = ' '.join([i.strip() for i in html.xpath("/html/body/div[2]/section/div/section[3]/div/div/div[2]/div/div/div[2]/div/div[2]/div/div[2]/div/div[1]/div/div[2]/ul/li/text()")]).strip().split(": $")[-1]
        list1['Year_acquisition'] = ' '.join([i.strip() for i in html.xpath("/html/body/div[2]/section/div/section[3]/div/div/div[2]/div/div/div[1]/div/div[2]/div/div[2]/div/div[1]/div/div[2]/ul/li/text()")]).strip().split(": $")[0]
        list1['Careers'] = re.sub("\s+",' ',' '.join([i.strip() for i in html.xpath("//h2[text()='Your career']/following-sibling::div/div/div/div[1]/div/p/span/text()")]).strip())
        list1['Credit'] = ''
        list1['Domestic_csp'] = ''
        list1['Course_structure'] = re.sub("\s+",' ',' '.join([i.strip() for i in html.xpath("//h2[text()='What you will study']/following-sibling::div/div/div/div[1]//text()")]).strip())
        try:
            list1['ATAR'] = html.xpath("//table[@class='table data-table-component responsive']/tbody/tr[last()]/td[last()]/text()")[0].strip()
        except:list1['ATAR'] = ''
        list1['Entry_requirements'] = ' '.join([i.strip() for i in html.xpath("/html/body/div[2]/section/div/section[12]/div[1]/div/div/div/div[2]/div/div/div/div/div/div/div/div/div/div/div[1]/div/div/div[2]//div[contains(@id,'rte')]/p//text()")]).strip()
        datas.append(list1)
        print(list1)


    def save(self):
        df = pd.DataFrame(datas)
        df.to_excel("flinders.xlsx",index = False)


if __name__ == '__main__':
    datas = []
    url = 'https://www.flinders.edu.au/study/courses'
    spider = Spider(url)
    spider.main()
    spider.save()