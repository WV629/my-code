#-*- coding:utf-8 -*-
# TODO : https://www.cdu.edu.au/study
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
                return res
        except:
            pass

def parse(url):
    html = etree.HTML(get_response(url).text)
    Facultys = html.xpath("//div[@class='image-tile--title']/text()")[:1]
    urls = html.xpath("//a[@class='image-tile']/@href")[:1]
    for Faculty,url in zip(Facultys,urls):
        html = etree.HTML(get_response(url).text)
        # Undergraduate
        divs = html.xpath("//h2[text()='Undergraduate study areas and courses']/../following-sibling::template[1]//div[@class='navigation-cards-text__item']")
        th = []
        for div in divs:
            study_area = div.xpath(".//div[@class='navigation-cards-text__title']/text()")[0]
            href = div.xpath(".//a/@href")[0]
            t = threading.Thread(target=parse1, args=(href,Faculty, 'Undergraduate', study_area))
            t.start()
            th.append(t)
        [t.join() for t in th]
        # Postgraduate
        divs = html.xpath("//h2[text()='Postgraduate study areas and courses']/../following-sibling::template[1]//div[@class='navigation-cards-text__item']")
        th = []
        for div in divs:
            study_area = div.xpath(".//div[@class='navigation-cards-text__title']/text()")[0]
            href = div.xpath(".//a/@href")[0]
            t = threading.Thread(target=parse1,args=(href,Faculty,'Postgraduate',study_area))
            t.start()
            th.append(t)
        [t.join() for t in th]


def parse1(href,Faculty, degree, study_area):
    list1 = {}
    html = etree.HTML(get_response(href).text)
    url = html.xpath("//a[text()='Visit the course page']/@href")
    if len(url)==0:
        return
    res = get_response(url[0])
    html = etree.HTML(res.text)
    list1['Faculty'] = Faculty
    list1['degree'] = degree
    list1['study_area'] = study_area
    list1['href'] = res.url
    list1['Course_name'] = ''.join(html.xpath("//h1/text()")).strip()
    list1['year_acquisition'] = ''.join(html.xpath("//h2[@id='overview']/span/text()")).strip()
    list1['Duration'] = ' '.join([i.strip() for i in html.xpath("//h3[text()=' Duration']/../following-sibling::dd/span/text()") if i.strip() !='']).strip()
    list1['Location'] = ';'.join([i.strip() for i in html.xpath("//h3[text()=' Location']/following-sibling::dl//text()") if i.strip() !='']).strip()
    list1['Desc'] = ''.join([i.strip() for i in html.xpath("//div[@class='richtext richtext__medium']//text()") if i.strip() !='']).strip()
    list1['Course_structure'] = ''.join([i.strip() for i in html.xpath("//div[@class='richtext richtext__medium']/node()[not(@id)]//text()") if i.strip() !='']).strip()
    try:
        list1['Credit'] = re.findall("[^\.\d](\d+\.\d+|\d+) credit",list1['Course_structure'],re.I)[0]
    except:
        list1['Credit'] = ''
    list1['Career'] = ''.join([i.strip() for i in html.xpath("//h2[@id='career-outcomes']/following-sibling::div[1]/div/div/div//text()") if i.strip() !='']).strip()
    list1['Entry_requirement'] = ''.join([i.strip() for i in html.xpath("//div[@id='c-entry-requirements' or @id='c-entry-eligibility']/div//text()") if i.strip() !='']).strip()
    try:
        list1['ATAR'] = re.findall("was (\d+\.\d+)",list1['Entry_requirement'])[0]
    except:
        list1['ATAR'] = ''
    list1['Domestic_csp'] = ''.join([i.strip() for i in html.xpath("//h4[text()='Domestic students']/following-sibling::div/div/div/p[position()>1]//text()") if i.strip() !='']).strip()
    list1['Domestic_full'] = ''
    list1['International_full'] = ''.join([i.strip() for i in html.xpath("//h4[text()='International students']/following-sibling::div//text()") if i.strip() !='']).strip()
    try:
        list1['International_full'] = re.findall("\$(\d+,\d+) AUD\*",list1['International_full'])[0]
    except:
        list1['International_full'] = ''
    datas.append(list1)
    print(list1)


if __name__ == '__main__':
    datas = []
    url = 'https://www.utas.edu.au/courses'
    print("start___________")
    parse(url)
    df = pd.DataFrame(datas)
    df.to_excel("tas.xlsx",index=False)