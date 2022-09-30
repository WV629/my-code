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
    for _ in range(10):
        try:
            res = requests.get(url,headers=headers,timeout=10)
            if res.status_code == 200:
                return res
        except:
            pass

def parse(url):
    html = etree.HTML(get_response(url).text)
    hrefs = html.xpath("//div[@class='online-degree-panel medium-up-2 large-up-4']/a/@href")
    Facltys = html.xpath("//div[@class='online-degree-panel medium-up-2 large-up-4']/a/span[2]/text()")
    th = []
    for href,Faclty in zip(hrefs,Facltys):
        href = urljoin(url,href)
        t = threading.Thread(target=parse1, args=(href,Faclty))
        t.start()
        th.append(t)
    [t.join() for t in th]


def parse1(href,Faclty):
    html = etree.HTML(get_response(href).text)
    # undergraduate
    trs = html.xpath("//span[contains(text(),'Undergraduate')]/../..//tr[position()>1]")
    if len(trs) != 0:
        parse2('Undergraduate',trs,Faclty)
    # postgraduate
    trs = html.xpath("//span[contains(text(),'Postgraduate')]/../..//tr[position()>1]")
    if len(trs) != 0:
        parse2('Postgraduate',trs,Faclty)
    # Research
    trs = html.xpath("//span[contains(text(),'Research')]/../..//tr[position()>1]")
    if len(trs) != 0:
        parse2('Research', trs, Faclty)


def parse2(Degree,trs,Faclty):
    for tr in trs:
        list1 = {}
        list1['Faclty'] = Faclty
        list1['Degree'] = Degree
        list1['Course_name'] = tr.xpath("./td[2]/a/text()")[0].strip()
        list1['Mode'] = tr.xpath("./td[3]/text()")[0].strip()
        href = urljoin(url,tr.xpath("./td[2]/a/@href")[0])
        list1['href'] = '/'.join(href.split("/")[:-1])+'/dom'
        print(list1['href'])
        html = etree.HTML(get_response(list1['href']).text)
        list1['Year_acquisition'] = ''.join(html.xpath("//div[@class='details all-text16']/p[2]/text()")).strip()
        list1['Location'] = ''.join(html.xpath("//span[contains(text(),'Campus')]/following-sibling::a/span[1]/text()")).strip()
        list1['Duration'] = ''.join(html.xpath("//span[contains(text(),'Duration')]/../text()")).strip()
        list1['ATAR'] = ''.join(html.xpath("//*[contains(text(),'Entry Scores')]/../text()")).strip().split("  ")
        if len(list1['ATAR']) != 1:
            list1['ATAR'] = list1['ATAR'][1].strip()
        else:list1['ATAR'] = ''
        list1['Domestic_full'] = ''.join(html.xpath("//span[contains(text(),'Fees')]/../a/span[1]/text()")).strip()
        if list1['Domestic_full'] == '':
            list1['Domestic_full'] = ''.join(html.xpath("//span[contains(text(),'Fees')]/../text()")).strip()
        list1['Desc'] = ''.join(html.xpath("//div[@class='columns wysiwyg-content two-col-list']/ul/li//text()")).strip()
        list1['Desc'] = re.sub('\s', ' ', list1['Desc'])
        list1['Entry_requirements'] = ''.join([i.strip() for i in html.xpath("//h2[text()='Entry requirements']/following-sibling::div//text()") if i.strip() != '']).strip()
        list1['Careers'] = ''.join([i.strip() for i in html.xpath("//h3[text()='Your career']/following-sibling::node()//text()") if i.strip() != '']).strip()
        list1['Careers'] = re.sub('\s',' ',list1['Careers'])
        list1['Course_structure'] = ' '.join([i.strip() for i in html.xpath("//h3[text()='Degree structure']/../following-sibling::table//text()") if i.strip() != '']).strip()
        list1['Credit'] = ''
        html = etree.HTML(get_response('/'.join(href.split("/")[:-1])+'/int').text)
        fee = ''.join(html.xpath("//span[contains(text(),'Fees')]/following-sibling::span/text()"))
        try:
            list1['International_fee'] = re.search("AUD\$ (.*?) per",fee).group(1)
        except:
            list1['International_fee'] = ''
        datas.append(list1)
        print(list1)



if __name__ == '__main__':
    datas = []
    url = 'https://study.unisa.edu.au/'
    print("start___________")
    parse(url)
    print("正在保存----------")
    df = pd.DataFrame(datas)
    df.to_excel("usa.xlsx",index=False)