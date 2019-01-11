#coding=utf-8
import pymysql
import requests
import pymongo
from lxml import etree
from car_info import CarInfo



MONGO_URI = 'localhost'
MONGO_DB = 'test' # 定义数据库
MONGO_COLLECTION = 'guazi' # 定义数据库表

class guazi_spider(object):
    car_dictionary = {}

    def __init__(self,mongo_uri,mongo_db):
        print("-----__init__------")
        #self.client = pymongo.MongoClient(mongo_uri)
        #self.db = self.client[mongo_db]

    def get_html(self,url):
        headers = {'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
           'Accept-Encoding':'gzip, deflate,br',
           'Accept-Language':'zh-CN,zh;q=0.9',
           'Cache-Control':'no-cache',
           'Connection':'keep-alive','Cookie':'antipas=613017j3554728836E64Fo669F6; uuid=8af19ed2-c371-449b-b4b6-f84796170f89; ganji_uuid=7897240256738313080932; cityDomain=sh; close_finance_popup=2019-01-10; clueSourceCode=%2A%2300; preTime=%7B%22last%22%3A1547100084%2C%22this%22%3A1546849832%2C%22pre%22%3A1546849832%7D; Hm_lvt_936a6d5df3f3d309bda39e92da3dd52f=1546852262,1546855364,1547091203,1547100083; Hm_lpvt_936a6d5df3f3d309bda39e92da3dd52f=1547100083; sessionid=33fd64bd-f79d-4cbf-ae18-2e00afb67b88; cainfo=%7B%22ca_s%22%3A%22seo_baidu%22%2C%22ca_n%22%3A%22default%22%2C%22ca_i%22%3A%22-%22%2C%22ca_medium%22%3A%22-%22%2C%22ca_term%22%3A%22-%22%2C%22ca_kw%22%3A%22-%22%2C%22keyword%22%3A%22-%22%2C%22ca_keywordid%22%3A%22-%22%2C%22scode%22%3A%22-%22%2C%22ca_b%22%3A%22-%22%2C%22ca_a%22%3A%22-%22%2C%22display_finance_flag%22%3A%22-%22%2C%22platform%22%3A%221%22%2C%22version%22%3A1%2C%22client_ab%22%3A%22-%22%2C%22guid%22%3A%228af19ed2-c371-449b-b4b6-f84796170f89%22%2C%22sessionid%22%3A%2233fd64bd-f79d-4cbf-ae18-2e00afb67b88%22%7D',
           'Host':'www.xin.com',
           'Pragma':'no-cache',
           'Referer':'https://www.xin.com/shanghai/s/',
           'Upgrade-Insecure-Requests':'1',
           'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'
           }
        raw_html = requests.get(url, headers=headers).text
        return raw_html

    def get_Start(self):
        url = 'https://www.xin.com/shanghai/s/'
        raw_html = self.get_html(url)
        selector = etree.HTML(raw_html)
        initial = selector.xpath('//ul[@class="brand-letter clearfix search-brand-letter"]//li/text()')
        initial.pop(0)
        
        i = 1;
        # setp1先遍历出首字母
        for inita_temp in initial:
            class_name = 'li_spell_' + inita_temp
            sourse_path = '//li[@class="li_spell li_spell_test"]//dl//dd/a'
            path = sourse_path.replace('li_spell_test', class_name)
            car_items = selector.xpath(path)
            # step2 遍历出具体车名
            for item in car_items:
                 car_info = CarInfo()
                 car_info.car_brand_id = i
                 car_info.car_brand_initial = inita_temp
                 car_info.car_brand_name = item.text.strip().strip('\n')
                 car_info.url = 'https:' + item.attrib['href']
                 self.car_dictionary[car_info.car_brand_name] = car_info
                 # 保存车品牌信息
                 save_sql = "insert into pm_car_brand(car_brand_id,car_brand_initial,car_brand_name)values({0},'{1}','{2}')"
                 save_sql = save_sql.format(car_info.car_brand_id,car_info.car_brand_initial, car_info.car_brand_name)
                 self.save_MySql(save_sql)
                 # 获取并保存车系信息
                 self.save_CarType(car_info)
                 i = i+1
                 print('--------' + car_info.car_brand_name)
    print('----end----')

    def save_CarType(self, car_info):
        raw_html = self.get_html(car_info.url)
        selector = etree.HTML(raw_html)
        car_items = selector.xpath('//ul[@class="series-category series-tpg no-float"]//div//li/a')
        for item in car_items:
            type_name = item.text.strip()
            save_sql = "insert into pm_car_train(car_train_name,car_brand_id)values('{0}',{1})"
            save_sql = save_sql.format(type_name,car_info.car_brand_id)
            self.save_MySql(save_sql)
        #print('****************end****************')

    def save_MySql(self,sql):
        connection = pymysql.connect(host='101.132.135.5', user='root', password='Chiju123!', db='bdtp',
                                     charset='utf8')
        cursor = connection.cursor()
        try:
            cursor.execute(sql)
            connection.commit()
        except Exception as e:
            print(e)
            connection.rollback()
        connection.close()

    def get_PageNumber(self):
        url = 'https://www.xin.com/shanghai/s/'
        raw_html = self.get_html(url)
        selector = etree.HTML(raw_html)
        #testurl = selector.xpath('//ul[@class="brand-cars clearfix"]//dl//dd/a/@href')
        #testname = selector.xpath('//ul[@class="brand-cars clearfix"]//dl//dd/a/text()')
        car_items = selector.xpath('//ul[@class="brand-cars clearfix"]//dl//dd/a')
        for item in car_items:
            car_key = item.text.strip().strip('\n')
            car_info = CarInfo() 
            car_info.car_brand_name = car_key
            car_info.url = 'https:' + item.attrib['href']
            self.car_dictionary[car_key] = car_value
            print(car_key + ':' + car_value)
        page_total = selector.xpath('//ul[@class="brand-cars clearfix"]//dl//dd/a/text()')
        return  page_total

    def get_AllPage(self,url):
        raw_html = self.get_html(url)
        selector = etree.HTML(raw_html)
        car_name = selector.xpath('//ul[@class="carlist clearfix js-top"]//li//h2/text()')
        car_price = selector.xpath('//ul[@class="carlist clearfix js-top"]//li//div[@class="t-price"]//p/text()')
        return car_name,car_price

    def Save_MongoDB(self,data):
        print("-----Save_MongoDB------")
        #self.db[MONGO_COLLECTION].insert_one(data)
        #self.client.close()

    def Get_Car_Url(self,car_name):
        print("-----Save_MongoDB------")

    def Save_Mysql(self,car_name,car_price):
        connection = pymysql.connect(host='localhost', user='root', password='123456', db='scrapydb',
                                     charset='utf8')
        try:
            for i in range(len(car_name)):
                with connection.cursor() as cursor:
                    sql = "insert into `guazi`(`汽车型号`,`汽车价格`)values(%s,%s)"
                    cursor.execute(sql, (car_name[i], car_price[i]))
            connection.commit()
        finally:
            connection.close()

guazi = guazi_spider(MONGO_URI,MONGO_DB)

page_total = guazi.get_Start()
# for page in range(1,int(page_total) + 1):
#     print("-----第" + str(page) + "页爬取开始------")
#     guazi_data = {}
#     url = 'https://www.guazi.com/cq/buy/o' + str(page) + '/#bread'
#     car_name,car_price = guazi.get_AllPage(url)
#     print(car_name)
#     print(car_price)
#     guazi_data["汽车型号"] = car_name
#     guazi_data["汽车价格"] = car_price
#     guazi.Save_MongoDB(guazi_data)
#     print(guazi_data)
#     guazi.Save_Mysql(car_name,car_price)
#     print("-----第" + str(page) + "页爬取结束------")

# print("------爬虫结束------")

