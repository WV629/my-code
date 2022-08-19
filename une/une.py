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


    def send_post(self,id):
        url = 'https://study.csu.edu.au/_web_services/ocb-metadata.js'
        data = {"id": id, "type": "getMetadata", "nonce_token": "e26bb83fb01e678a0a34ec58c42b771d5cf74fd8"}
        headers = {
            'X-SquizMatrix-JSAPI-Key': '9216575650',
            'Cookie': 'NSC_JO3mew5jdqcgtuydyxeqt2dz0tmjccq=ffffffff090c41b845525d5f4f58455e445a4a4229a0; check=true; AMCVS_4E0C5990589C5D5D0A495DDD%40AdobeOrg=1; s_ecid=MCMID%7C62331073542848792434115991891614975390; _gcl_au=1.1.1240573551.1660280204; s_cc=true; _cs_c=1; aam_uuid=62131917499406919634154344390619655150; _gid=GA1.3.1085339529.1660280212; _mkto_trk=id:075-KSK-811&token:_mch-csu.edu.au-1660280212059-64242; cebs=1; _ce.s=v~f968118d3d7681becae5521d51847d47557ef19a~vpv~0; _clck=15sy27p|1|f3y|0; SQ_SYSTEM_SESSION=o4l52bvtaq9lcibvhhiebq61q4bor175echcvlim52v1646r3n4qqkcqf9j6aua2iu5g0rqerg4kguumgt1mb09vcnlnb62paefp2f1; NSC_JO03wk40ep1h5nkd4glyied3wklshbq=ffffffff090c41b845525d5f4f58455e445a4a423660; futureStudents_courseId=4220AG; s_ips=569; _tt_enable_cookie=1; _ttp=f1837dd7-f2c7-4ab4-ba3c-df18dc47243a; s_tp=569; adcloud={%22_les_v%22:%22y%2Ccsu.edu.au%2C1660308238%22}; s_vnum=1660406400291%26vn%3D3; s_invisit=true; _cs_mk_aa=0.8437321095864809_1660306441441; s_sq=%5B%5BB%5D%5D; AMCV_4E0C5990589C5D5D0A495DDD%40AdobeOrg=-1124106680%7CMCIDTS%7C19217%7CMCMID%7C62331073542848792434115991891614975390%7CMCAAMLH-1660911241%7C11%7CMCAAMB-1660911241%7CRKhpRz8krg2tLO6pguXWp5olkAcUniQYPHaMWWgdJ3xzPWQmdj0y%7CMCOPTOUT-1660313641s%7CNONE%7CMCAID%7CNONE%7CvVersion%7C5.2.0; s_ppv=404%253Ahttps%253A%2F%2Fstudy.csu.edu.au%2Fcourses%2Fagricultural-wine-sciences%2Fassociate-degree-farm-production%2C100%2C100%2C569%2C1%2C1; _cs_id=62e2ff55-33da-a5ae-ba94-1d200688fd82.1660280204.3.1660306441.1660306441.1.1694444204778; _uetsid=2a0ce9a019fb11eda4ff472e0d4f7ab7; _uetvid=2a0d55f019fb11edbefb639de80532d4; _cs_s=1.5.0.1660308242998; cebsp=16; _clsk=1o1mktq|1660306447544|2|1|k.clarity.ms/collect; _ga_09603PQVTC=GS1.1.1660306440.4.1.1660306641.0; _ga=GA1.3.1032682367.1660280209; s_nr=1660306660899-Repeat; mbox=PC#3cd7e58677a14cb597400c1e87b9ab77.32_0#1723543179|session#6b7b787022fa4d70bd088806110539cf#1660308638',
        }
        r = requests.post(url, data=data, headers=headers).json()
        return r

    def save(self):
        df = pd.DataFrame(datas)
        df.to_excel("une.xlsx",index = False)


if __name__ == '__main__':
    datas = []
    url = 'https://www.une.edu.au/study'
    spider = Spider(url)
    spider.main()
    spider.save()