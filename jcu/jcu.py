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
    lis = html.xpath("//ul[@class='jcu-v1__ct__link-list__container']/li/a")
    i = 1
    for li in lis:
        Faculty = li.xpath("./text()")[0].strip()
        href = urljoin(url,li.xpath("./@href")[0])
        html = get_response(href)
        divs = html.xpath("//div[@class='jcu-v1__block__column']/div[1][@class='jcu-v1__ct__usp']/div/div")
        if i==7:
            i = i + 1
            for div in divs:
                course_name = div.xpath(".//h3/text()")[0]
                course_url = div.xpath("./a/@href")[0]
                degree = ''
                run(course_name,course_url,degree,Faculty)
        if len(divs) != 0:
            for div in divs:
                Faculty = div.xpath(".//h3/text()")[0].strip()
                if Faculty.startswith("#"):
                    continue
                parse1(Faculty)
        else:
            parse1(Faculty)
        print(i)
        i = i+1
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
        list1['Entry_requirements'] = ' '.join(html.xpath("//h2[text()='Admission Requirements']/following-sibling::table//text()")).strip()
        Entry_requirements = ''.join(html.xpath("//*[text()='Credit points']/../../following-sibling::td//text()")).strip()
        if 'credit points' in Entry_requirements:
            list1['Entry_requirements'] = Entry_requirements.split(" ")[0]
        if list1['Location']=='' and list1['ATAR']=='' and list1['International_full']=='' and list1['Desc']=='' and list1['Careers']=='' and  list1['Course_code']=='' and list1['Entry_requirements']=='':
            return
        print(list1)
        datas.append(list1)



if __name__ == '__main__':
    datas = []
    url = 'https://www.jcu.edu.au/courses/undergraduate'
    print("start___________")
    parse(url)
    df = pd.DataFrame(datas)
    df.to_excel("jcu.xlsx",index=False)
