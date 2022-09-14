#-*- coding:utf-8 -*-
# TODO : https://www.usc.edu.au/study/courses-and-programs
import re
import threading
from urllib.parse import urljoin
import requests
from concurrent.futures import ThreadPoolExecutor
from lxml import etree
from threading import Thread
import pandas as pd



def get_response(url):
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36'
    }
    for _ in range(5):
        try:
            res = requests.get(url,headers=headers,timeout=10)
            if res.status_code == 200:
                return etree.HTML(res.text)
        except:
            pass

def parse(url):
    html = get_response(url)
    Facultys = html.xpath("//ul[@class='button-list']/li/a/span/text()")
    urls = ['https://www.usc.edu.au'+i for i in html.xpath("//ul[@class='button-list']/li/a/@href")]
    for Faculty,url in zip(Facultys,urls):
        html = get_response(url)
        h5s = html.xpath("//div[@class='program-list--container']//h5")
        for h5 in h5s:
            degree = h5.xpath("./text()")[0]
            courses = h5.xpath("./following-sibling::ul/li/a")
            for course in courses:
                list1 = {}
                list1['Faculty'] = Faculty
                list1['Degree'] = degree
                list1['Course_name'] = course.xpath("./text()")[0]
                list1['href'] = 'https://www.usc.edu.au'+course.xpath("./@href")[0]
                html = get_response(list1['href'])
                list1['Desc'] = ' '.join([i.strip() for i in html.xpath("//div[@ audience='domestic international']//text()") if i != '' or i != ' ']).strip()
                list1['Desc'] = re.sub('\s+',' ',list1['Desc'])
                list1['Location'] = '; '.join([i.strip() for i in html.xpath("//div[@id='locationDropdown']/button/text()")])
                list1['ATAR'] = ''.join(html.xpath("//small[text()='ATAR/Rank']/preceding-sibling::strong[last()]/text()")).strip()
                year = ''.join(html.xpath("//strong[@audience='domestic']/text()")).strip()
                tt = ''.join(html.xpath("//small[@class='summary-footnote --small' and @audience='domestic']/text()")).strip()
                if  tt == '':
                    tt = ''.join(html.xpath("//small[@class='summary-footnote --small' and @audience='international']/text()")).strip()
                list1['Duration'] = year + ' ' + tt
                list1['Domestic_csp'] = ''.join(html.xpath("//div[@audience='domestic' and @class='--button-last']/strong/text()")).strip().replace("A$",'')
                list1['Mode'] = ''.join(html.xpath("//span[contains(text(),'Delivery mode')]/../following-sibling::dd[1]//text()")).strip()
                list1['Credit'] = ''.join(html.xpath("//dt[contains(text(),'Total courses')]/following-sibling::dd[1]//text()")).strip()
                list1['Careers'] = '; '.join(html.xpath("//h4[text()='Career opportunities']/following-sibling::ul/li//text()")).strip()
                list1['Course_code'] = ''.join(html.xpath("//h3[text()='CRICOS code']/following-sibling::div[1]/strong/text()")).strip()
                list1['International_full'] = ''.join(html.xpath("//div[@class='--button-last' and @audience='international']/strong/text()")).strip().replace("A$",'')
                if '-' in list1['International_full']:
                    list1['International_full'] = list1['International_full'].split("-")[0].strip()
                elif '/' in list1['International_full']:
                    list1['International_full'] = list1['International_full'].split("/")[0].strip()
                h4 = html.xpath("//div[@class='program-detail']//div[@audience='international']/h4")
                if len(h4) == 1:
                    list1['Entry_requirements'] = ''.join(html.xpath("//h4[text()='Entry requirements']/following-sibling::p/text()")).strip()
                else:
                    list1['Entry_requirements'] =''.join(html.xpath("//h4[text()='Entry requirements']/following-sibling::p[position()<=(count(//div[@class='program-detail']//div[@audience='international']/h4[1]/following-sibling::p)-count(//div[@class='program-detail']//div[@audience='international']/h4[2]/following-sibling::p))]/text()")).strip()
                list1['Entry_requirements'] = re.sub('\s',' ',list1['Entry_requirements'])
                datas.append(list1)
                print(list1)
                print("*"*50)


if __name__ == '__main__':
    datas = []
    url = 'https://www.usc.edu.au/study/courses-and-programs'
    print("start___________")
    parse(url)
    df = pd.DataFrame(datas)
    df.to_excel("usc.xlsx",index=False)
