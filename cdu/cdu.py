#-*- coding:utf-8 -*-
# TODO : https://www.cdu.edu.au/study
import re
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
    for _ in range(3):
        try:
            res = requests.get(url,headers=headers)
            if res.status_code == 200:
                return etree.HTML(res.text)
        except:
            pass

def parse(url):
    html = get_response(url)
    lis = html.xpath("//li[@class='field-item study-area-listing__item']")
    th = []
    for li in lis:
        faculty = li.xpath("./a/text()")[0]
        href = urljoin(url,li.xpath("./a/@href")[0])
        t = Thread(target=parse1,args=(href,faculty))
        t.start()
        th.append(t)
    [t.join() for t in th]

def parse1(url,faculty):
    html = get_response(url)
    degree_names = html.xpath("//ul[@class='tab-list']//div[@class='tab-list__title']/text()")
    index = 1
    for degree_name in degree_names:
        divs = html.xpath(f"//div[@class='js-tab-list container--no-spacing-bottom study-area']/section[{index}]/div/div[2]/div/div/div/a")
        for div in divs:
            list1 = {}
            list1['Faculty'] = faculty
            list1['Degree'] = degree_name
            list1['Course_name'] = div.xpath("./text()")[0]
            list1['href'] = urljoin(url,div.xpath("./@href")[0])
            list1['Duration'] = '; '.join(div.xpath("./../../../div[2]//div[@class='copy--s']/text()"))
            list1['Location'] = ';'.join(div.xpath("./../../../div[3]/div[@data-student-type='domestic']/text()")).split(",")[0]
            try:
                list1['Mode'] = ';'.join(div.xpath("./../../../div[3]/div[@data-student-type='domestic']/text()")).split(",")[1]
            except:
                list1['Mode'] = ''

            html1 = get_response(list1['href'])
            list1['Credit'] = ''.join(html1.xpath("//h3[text()='Credit points required']/../text()"))
            list1['Desc'] = '\n'.join(html1.xpath("//div[contains(@class,'overview')]//text()"))
            list1['Domestic_full'] = ''.join(html1.xpath("//h4[text()='Commonwealth supported places']/following-sibling::p//text()"))
            list1['Entry_requirements'] = ''.join(html1.xpath("//summary[@id='accordion-admission-criteria']/following-sibling::div//text()"))+''.join(html1.xpath("//summary[@id='accordion-essential-requirements']/following-sibling::div//text()"))
            list1['ATAR'] = ''.join(html1.xpath("//summary[@id='accordion-admission-criteria']/following-sibling::div//strong/text()")).replace("*",'')
            list1['course_structure'] = ''.join(html1.xpath("//*[@id='accordion-course-structure']/following-sibling::div//text()"))
            international_full = ''.join(html1.xpath("//*[@id='accordion-fees']/following-sibling::div/div[@data-student-type='international']//text()"))
            list1['International_full'] = ''.join(re.findall("AUD  \$(.*?)\.",international_full))
            datas.append(list1)
            print(list1)
        index = index + 1



if __name__ == '__main__':
    datas = []
    url = 'https://www.cdu.edu.au/study'
    print("start___________")
    parse(url)
    df = pd.DataFrame(datas)
    df.to_excel("cdu.xlsx",index=False)
