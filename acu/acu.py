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
import requests
import re
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
        if res.status_code != 200:
            res = requests.get(url.replace("https://www.acu.edu.au","https://online.acu.edu.au"), headers=self.headers)
        html = etree.HTML(res.content.decode())
        return html

    def get_res(self,url):
        res = requests.get(url,headers = self.headers)
        if res.status_code != 200:
            res = requests.get(url.replace("https://www.acu.edu.au", "https://online.acu.edu.au"), headers=self.headers)
        return res.json()

    def main(self):
        html = self.get_html(self.url)
        lis = html.xpath("//section[@class='Search-result-tiles desktop-width']/ul[@role='list']/li")
        for li in lis:
            department = li.xpath("./div/a/@title")[0]
            href = 'https://www.acu.edu.au//webapi/GetCourseResult/get?Citizenship=Domestic&StudyArea='+department
            CoursesResults = self.get_res(href)['CoursesResults']
            th = []
            for coursesResult in CoursesResults:
                 t =Thread(target=self.main1,args=(coursesResult,department))
                 t.start()
                 th.append(t)
            [t.join() for t in th]

    def main1(self,coursesResult,department):
        list1 = {}
        list1['department'] = department
        list1['CourseName'] = coursesResult['CourseName']
        coursesUrl = coursesResult['URL']
        list1['degree'] = coursesResult['Level']
        try:
            list1['ATAR'] = coursesResult['locations'][0]['Score']
        except:
            list1['ATAR'] = ''
        list1['coursesUrl'] = 'https://www.acu.edu.au' + coursesUrl
        html = self.get_html(list1['coursesUrl'])
        list1['location'] = ''.join(html.xpath("//select[@id='location']/option[@selected]/text()"))
        session = html.xpath("//h2[@class='h3 filtered-tldr__h1 margin-top--1 margin-bottom--1']/text()")[0]
        list1['session'] = re.findall("(\d{4})",session)[0]
        list1['studymode'] = ''.join(html.xpath("//dt[text()='Study mode']/following-sibling::dd[1]/text()"))
        a = ''.join(html.xpath("//dt[contains(text(),'Fees')]/following-sibling::dd[1]//text()"))
        if 'CSP' in a and 'paying' in a:
            print(a)
            list1['domestic_full'] = a.split(" CSP")[0].replace("$",'')
            list1['domestic_csp'] = a.split(" CSP")[1].replace(' Fee-paying','').replace('$','')
        elif 'CSP' in a:
            list1['domestic_full'] = ''
            list1['domestic_csp'] = a.replace(' CSP','').replace('$','')
        else:
            list1['domestic_full'] = a.replace(' Fee-paying','').replace('$','')
            list1['domestic_csp'] = ''
        new_url = list1['coursesUrl'] + '?type=International'
        international_html = self.get_html(new_url)
        list1['international_fee'] = ''.join(
            international_html.xpath("//dt[contains(text(),'Fees')]/following-sibling::dd[1]//text()")).replace('$','')
        list1['overview'] = ' '.join(
            [i.strip() for i in html.xpath("//div[@id='overview-description']//text()") if i != '']).strip()
        list1['domestic_entry_requirement'] = ' '.join(
            [i.strip() for i in html.xpath("//div[@id='entryrequirements']//text()") if i != '']).strip().replace(
            "Entry requirements", '').replace("   Expand all    ",'')
        list1['international_entry_requirement'] = ' '.join(
            [i.strip() for i in international_html.xpath("//div[@id='entryrequirements']//text()") if
             i != '']).strip().replace("Entry requirements", '').replace("   Expand all    ",'')
        list1['Careers'] = '\n'.join(
            [i.strip().replace("\n", '') for i in html.xpath("//h2[text()='Careers']/following-sibling::div//text()") if
             i != ''])
        print(list1)
        print("*" * 50)
        datas.append(list1)

    def save(self):
        df = pd.DataFrame(datas)
        df.to_excel("acu.xlsx",index = False)


if __name__ == '__main__':
    datas = []
    url = 'https://www.acu.edu.au/study-at-acu/find-a-course'
    spider = Spider(url)
    spider.main()
    spider.save()