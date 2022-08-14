#-*- coding:utf-8 -*-
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
        lis = html.xpath("//div[@class='arrow-list max-cols-3 ']/ul/li")
        for li in lis:
            faculty = li.xpath("./a/text()")[0]
            href = li.xpath("./a/@href")[0]
            if href.startswith("//"):
                href = href.replace("//", 'http://')
            html = self.get_html(href)
            hrefs = html.xpath("//h2[text()='Browse by interest area']/following-sibling::section[1]//a/@href")
            th = []
            for href in hrefs:
                # self.main1(href,faculty)
                 t =Thread(target=self.main1,args=(href,faculty))
                 t.start()
                 th.append(t)
            [t.join() for t in th]

    def main1(self,href,faculty):
        if href.startswith("//"):
            href = href.replace("//",'http://')
        html = self.get_html(href)
        uls = html.xpath("//div[contains(@class,'study-at-scu-choice transition-all')]/div/h2")
        for ul in uls:
            degree = ul.xpath("./text()")[0]
            lis = ul.xpath("./following-sibling::ul/li")
            for li in lis:
                list1 = {}
                list1['faculty'] = faculty
                list1['degree'] = degree
                print(href)
                list1['course name'] = li.xpath("./a/text()")[0].strip()
                list1['url'] = li.xpath("./a/@href")[0].replace("\n",'').strip()
                if list1['url'].startswith("//"):
                    list1['url'] = list1['url'].replace("//",'http://')
                html = self.get_html(list1['url'])
                list1['ATAR'] = ''.join(html.xpath("//span[text()='ATAR']/../following-sibling::dd[1]/text()"))
                list1['Duration'] = ''.join(html.xpath("//span[text()='Duration']/../following-sibling::dd[1]/text()")).replace('\r\n','').strip()
                list1['Location'] = ''.join(html.xpath("//span[text()='Location']/../following-sibling::dd[1]/text()")).replace('\r\n','').strip()
                list1['Domestic fee'] = ''.join(html.xpath("//dd[@class='show-domestic']/a/text()"))
                list1['session'] = ';'.join(re.findall("(\d{4})",''.join(html.xpath("//p[@class='ml-lg-auto course-year-links']//text()"))))
                list1['overview'] = ''.join([i.strip() for i in html.xpath("//div[@id='course-overview']/following-sibling::div[1]//text()") if i != ''])
                list1['Entry requirement'] = ''.join([i.strip() for i in html.xpath("//*[@id='credit-prior-learning']/following-sibling::p//text()") if i != ''])
                trs = html.xpath("//p[text()='International students']/following-sibling::table/tbody/tr")
                if len(trs)!=0:
                    for tr in trs[:-1]:
                        try:
                            list1[tr.xpath("./td[1]/text()")[0].strip()+'_international_fee'] = tr.xpath("./td[3]/text()")[0].split(" ")[0].replace("$",'')
                        except:pass
                if list1['ATAR']=='' and list1['Duration']=='' and list1['Location'] =='' and list1['Domestic fee']=='' and list1['session']==''and list1['overview']=='':
                    with open("a.txt",'a',encoding='utf-8') as f:
                        f.write(list1['url']+'\n\n')
                    continue
                print(list1)
                print("*" * 50)
                datas.append(list1)

    def save(self):
        df = pd.DataFrame(datas)
        df.to_excel("scu.xlsx",index = False)


if __name__ == '__main__':
    datas = []
    url = 'https://www.scu.edu.au/study-at-scu/'
    spider = Spider(url)
    spider.main()
    spider.save()