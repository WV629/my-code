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


def parse1(Faculty):
    print(Faculty)
    if Faculty == 'Teaching and Education':
        Faculty1 = 'Education'
    else:Faculty1 = Faculty
    url = 'https://www.jcu.edu.au/courses/_config/ajax-items/global-funnelback-results-dev'
    params = {
        'collection': 'jcu-v1-courses',
        'query': '!null',
        'num_ranks': '1000',
        'pagination': 'false',
        'sort': 'metacourseSort',
        'meta_studyArea_sand': Faculty1,
        'meta_courseAvailability_orsand': 'both dom_only',
        'meta_studyLevel_sand': 'Undergraduate'
    }
    params1 = {
        'collection': 'jcu-v1-courses',
        'query': '!null',
        'num_ranks': '1000',
        'pagination': 'false',
        'sort': 'metacourseSort',
        'meta_studyArea_sand': Faculty1,
        'meta_courseAvailability_orsand': 'both dom_only',
        'meta_studyLevel_sand': 'Post-Graduate'
    }
    parse_detail(url,params,'Undergraduate',Faculty)
    parse_detail(url,params1,'Postgraduate',Faculty)
    # t1 = threading.Thread(target=parse_detail,args=(url,params,'Undergraduate',Faculty))
    # t2 = threading.Thread(target=parse_detail,args=(url,params1,'Postgraduate',Faculty))
    # t1.start()
    # t2.start()


def parse_detail(url,params,degree,Faculty):
    res = requests.get(url,params=params,headers={'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36'}).content.decode()
    html = etree.HTML(res)
    course_names = html.xpath("//div[@class='jcu-v1__search__result--title']/a/text()")
    course_urls = html.xpath("//div[@class='jcu-v1__search__result--title']/a/@href")
    if len(course_names) != 0:
        th = []
        for course_name,course_url in zip(course_names,course_urls):
            t = threading.Thread(target=run,args=(course_name,course_url,degree,Faculty))
            t.start()
            th.append(t)
        [t.join() for t in th]

def run(course_name,course_url,degree,Faculty):
    list1 = {}
    list1['Faculty'] = Faculty
    list1['Degree'] = degree
    list1['Course_name'] = course_name
    list1['href'] = course_url
    html = get_response(course_url)
    if html is not None:
        list1['Location'] = ';'.join([i.strip() for i in html.xpath("//h4[text()='Location']/../following-sibling::div//ul/li//a/text()")]).strip()
        list1['Duration'] = ' '.join([i.strip() for i in html.xpath("//h4[text()='Duration']/../following-sibling::div//p/text()")]).strip()
        list1['ATAR'] = ''.join(html.xpath("//h4[text()='Entry Requirements']/../following-sibling::div//strong/text()")).strip().replace("ATAR ",'')
        Fee = ''.join(html.xpath("//h4[text()='Fees']/../following-sibling::div//p/text()")).strip()
        if len(html.xpath("//h4[text()='Fees']/../following-sibling::div//*[contains(text(),'$')]")) == 2:
            list1['Domestic_csp'] = html.xpath("//h4[text()='Fees']/../following-sibling::div//*[contains(text(),'$')]/text()")[0].strip().replace("$",'')
            list1['Domestic_full'] = html.xpath("//h4[text()='Fees']/../following-sibling::div//*[contains(text(),'$')]/text()")[1].strip().replace("$",'')
        elif 'Commonwealth Supported' in Fee:
            list1['Domestic_csp'] = ''.join(html.xpath("//h4[text()='Fees']/../following-sibling::div//*[contains(text(),'$')]/text()")).strip().replace("$",'')
        elif len(html.xpath("//h4[text()='Fees']/../following-sibling::div//*[contains(text(),'$')]")) == 1:
            list1['Domestic_full'] = ''.join(html.xpath("//h4[text()='Fees']/../following-sibling::div//*[contains(text(),'$')]/text()")).strip().replace("$",'')
        new_url = course_url + '?international'
        html = get_response(new_url)

        list1['International_full'] = ''.join(html.xpath("//h4[text()='Fees']/../following-sibling::div//*[contains(text(),'$')]/text()")).strip().replace("$", '')
        try:
            if list1['Domestic_csp'] + list1['Domestic_full'] == list1['International_full']:
                list1['International_full'] = ''
        except:pass
        list1['Desc'] = ''.join(html.xpath("//p[@class='course-banner__text']/text()")).strip()
        list1['Careers'] = re.sub("\s",' ',''.join(html.xpath("//div[@id='accordion_career']//p/text()")).strip())
        list1['Course_code'] = ''.join(html.xpath("//*[contains(text(),'ourse') and contains(text(),'ode')]/../../following-sibling::td/p/text()")).strip()
        list1['Entry_requirements'] = re.sub("\s",' ',' '.join(html.xpath("//h2[text()='Admission Requirements']/following-sibling::table//text()")).strip())
        credit_points = ''.join(html.xpath("//*[text()='Credit points']/../../following-sibling::td//text()")).strip()
        if 'credit points' in credit_points:
            list1['Credit'] = credit_points.split(" ")[0]
        if list1['Location']=='' and list1['ATAR']=='' and list1['International_full']=='' and list1['Desc']=='' and list1['Careers']=='' and  list1['Course_code']=='' and list1['Entry_requirements']=='':
            return
        print(list1)
        datas.append(list1)



if __name__ == '__main__':
    datas = []
    url = 'https://www.usc.edu.au/study/courses-and-programs'
    print("start___________")
    parse(url)
    df = pd.DataFrame(datas)
    df.to_excel("usc.xlsx",index=False)
