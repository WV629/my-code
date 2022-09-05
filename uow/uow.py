import requests
from lxml import etree
from threading import Thread
import pandas as pd



# TODO : https://www.uow.edu.au/study/
def parse(li,faculy,degrees,url):
    list1 = {}
    list1['faculy'] = faculy
    list1['degrees'] = degrees.replace("\r", '').replace("\n", '').replace("\t", '').strip()
    list1['course_name'] = li.xpath(".//a/text()")[0]
    list1['href'] = li.xpath(".//a/@href")[0]
    # print(list1['href'])
    res = requests.get(list1['href']).content.decode()
    # print(res)
    if 'Course not found' in res:
        return
    html = etree.HTML(res)
    list1['desc'] = ''.join(
        [i.strip() for i in html.xpath("//h2[text()='Course summary']/following-sibling::div//text()")])
    list1['study area'] = ''.join(html.xpath("//p[text()='Study area']/following-sibling::p/text()")).strip()
    list1['location'] = ''.join(html.xpath("//p[text()='Campus']/following-sibling::p/text()")).strip()
    list1['course code'] = ''.join(html.xpath("//p[text()='Course Code']/following-sibling::p/text()")).strip()
    list1['mode'] = ''.join(html.xpath("//p[text()='Delivery']/following-sibling::p/text()")).strip()
    list1['ATAR'] = ''.join(html.xpath("//*[text()='ATAR-SR ']/../following-sibling::p[1]/text()")).strip()
    list1['careers'] = '; '.join(
        html.xpath("//*[text()='Career opportunities']/following-sibling::ul/li/text()")).strip()
    print(list1)
    print("*" * 50)
    trs = html.xpath("//h4[@id='intl-fees']/following-sibling::div//table/tr")
    print(len(trs))
    if len(trs) != 0 :
        for tr in trs:
            list1['international_location'] = tr.xpath("./td[1]/p/text()")[0]
            list1['international_mode'] = tr.xpath("./td[2]/p/text()")[0]
            list1['international_session_fee'] = tr.xpath("./td[3]/p/text()")[0]
            list1['international_full'] = tr.xpath("./td[4]/p/text()")[0]
    list1['international_csp'] = ''.join(html.xpath("//h4[@id='intl-fees']/following-sibling::div/div/p//text()"))

    trs = html.xpath("//h4[@id='dom-fees']/following-sibling::div//table/tr")
    print(len(trs))
    if len(trs) != 0:
        for tr in trs:
            list1['domestic_location'] = tr.xpath("./td[1]/p/text()")[0]
            list1['domestic_mode'] = tr.xpath("./td[2]/p/text()")[0]
            list1['domestic_session_fee'] = tr.xpath("./td[3]/p/text()")[0]
            list1['domestic_full'] = tr.xpath("./td[4]/p/text()")[0]
    list1['domestic_csp'] = ''.join(html.xpath("//h4[@id='dom-fees']/following-sibling::div/p//text()"))
    datas.append(list1)

if __name__ == '__main__':
    datas = []
    url = 'https://www.uow.edu.au/study//motivation-data.json'
    Areas = requests.get(url).json()['Study Areas']
    for Area in Areas:
        try:
            faculy = Area['Name']
        except:
            break
        url = Area['URL']
        html = etree.HTML(requests.get(url).content.decode())
        degrees = html.xpath("//section[@class='page-content uw-responsive-accordion-tabs uw-responsive-accordion-tabs--grey']/div/ul/li[1]/a/text()")[0]
        lis = html.xpath("//section[@class='page-content uw-responsive-accordion-tabs uw-responsive-accordion-tabs--grey']/div/div[2]/div[1]/div/div/ul[1]/li")
        th = []
        for li in lis:
            t = Thread(target=parse,args=(li,faculy,degrees,url))
            t.start()
            th.append(t)
        [t.join() for t in th]
    df = pd.DataFrame(datas)
    df.to_excel("uow.xlsx",index=False)
