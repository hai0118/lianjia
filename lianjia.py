import time
from MysqlHelper import *
from brower import share_browser
from lxml import etree


class Spider(object):
    def __init__(self):
        self.browser = share_browser.share_browser()
        # self.l = []
        self.mysql = MysqlHelper('localhost', 3306, 'lianjia', 'root', 'xiangjia')

    def run(self):
        li_url = self.handle_url()
        for url in li_url:
            html = self.handle_etree(url)
            self.handle_data(html)
        # print(self.l)
        # print(len(self.l))

    def handle_etree(self, url):
        self.browser.get(url)
        html = etree.HTML(self.browser.page_source)
        # js = "var q=document.getElementByclassName('overlau_close').click()"
        time.sleep(3)
        # try:
        #     self.browser.find_element_by_class_name('overlau_close').click()
        # except Exception as e:
        #     print(e)
        # self.browser.execute_script(js)
        with open('tets.html', "w", encoding='utf-8') as fp:
            fp.write(self.browser.page_source)
        return html

    def handle_data(self, html):
        # print('handle-data')
        all = html.xpath("//ul[@class='sellListContent']/li")
        for one in all:
            i = {}
            i['title'] = one.xpath('.//div/div/a/text()')[0]
            image = one.xpath('./a/img/@src')[0]
            if not image.endswith('.jpg'):
                image = one.xpath('./a/img/@data-original')[0]
            i['image'] = image
            price = one.xpath(".//div[@class='totalPrice']/span/text()")[0]
            unit = one.xpath(".//div[@class='totalPrice']/text()")[0]
            i['price'] = str(price) + unit
            detail = one.xpath('./a/@href')[0]
            # print(detail)
            html = self.handle_etree(detail)
            self.handle_detail(html, i)

    def handle_detail(self, html, i):
        for n in html.xpath("//div[@class='overview']/div[@class='content']"):
            i['house_type'] = n.xpath("./div[@class='houseInfo']/div[@class='room']/div[@class='mainInfo']/text()")[0]
            i['areas'] = n.xpath("./div[@class='houseInfo']/div[@class='area']/div[@class='mainInfo']/text()")[0]
            phone = n.xpath("./div[@class='brokerInfo clear']//div[@class='phone']/text()")
            i['phone'] = '转'.join(phone)
        print(i)
        # self.l.append(i)
        self.write_mysql(i)


    def write_mysql(self, i):
        li = []
        for v in i.values():
            li.append(v)
        params = tuple(li)
        print(params)
        sql = 'insert into lianjia(title, image, price, house_type, areas, phone) VALUES(%s, %s, %s, %s, %s, %s)'
        self.mysql.insert(sql, params=params)
        print(i['title'] + '写入成功')

    def handle_url(self):
        url = 'https://bj.lianjia.com/ershoufang/pg'
        page = int(input('请输入要爬取的页数'))
        li = []
        for p in range(1, page + 1):
            finall_url = url + str(p)
            li.append(finall_url)
        return li

    def close(self):
        self.browser.quit()


s = Spider()
s.run()
s.close()
