#encoding:utf-8
"""
@project = untitled2
@file = jiepaiTest
@author = Administrator
@create_time = 2018/4/11 15:28
"""
import re
import requests
import json
import time
import os
import bs4
import pymongo
from multiprocessing import Pool
from requests import RequestException
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from pyquery import PyQuery as pq
from hashlib import md5
from infoConfig import *
from mongoConf import *


def getMongo():
    client=pymongo.MongoClient(MONGO_URL)
    return client[MONGO_DB]


def getJsView(url):
    driver = webdriver.PhantomJS()
    driver.get(url)
    return driver.page_source

def getJsChromeView(url):
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    driver = webdriver.Chrome(chrome_options=chrome_options)
    driver.get(url)
    return driver.page_source

def getTitle(url,param):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36"}
        resp=requests.get(url, param, headers=headers)
        if resp.status_code==200:
            return resp.text
        else:
            return None
    except RequestException:
        print("title fail", url, param)
        return getTitle(url, param)

def getIconFile(url,param):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36"}
        resp=requests.get(url,param,headers=headers)
        if resp.status_code==200:
            return resp.content
        else:
            return None
    except RequestException:
        print("title fail",url,param)
        return None

def getTitleData(titles):
    if titles != None:
        datas = json.loads(titles)
        # print(data)
        for datatemp in datas.get('data'):
            try:
                if datatemp.get('title'):
                    #print(datatemp)
                    yield {
                        'title': datatemp.get('title'),
                        'iconUrl': datatemp.get('url'),
                        'createTime': time.time(),
                        'updateTime': time.time()
                    }
                else:
                    pass
            except AttributeError:
                pass
    else:
        return None

def getUrlList(urldata,urltemp):
    pattern = re.compile('.*?&lt;/p&gt;&lt;p&gt;&lt;img src&#x3D;&quot;(.*?)&quot; ', re.S)
    url = re.findall(pattern,urldata)
    if len(url)==0:
        html = getJsChromeView(urltemp)
        doc=pq(html)
        li_em=doc.find('.image-list .image-item')
        listIconUrl=[]
        for listemp in li_em.items():
            div_em = listemp.find('.image-item-inner')
            img_em = div_em.children()
            srctemp = img_em[0].attrib
            print(srctemp.get('data-src'))
            listIconUrl.append(srctemp.get('data-src'))
        return listIconUrl
    else:
        return url


def write_to_file(url, file):
    dirfile= '{0}/{1}.{2}'.format(file, md5(url.encode('utf-8')).hexdigest(), 'jpg')
    print(dirfile)
    if os.path.isfile(dirfile):
        pass
    else:
        file=getIconFile(url,None)
        if file!=None:
            with open(dirfile,'wb') as f:
                f.write(file)
                f.close()
        else:
            print('save icon fail'+url)


def getIconUrl(datas):
    for data in datas:
        urldata= getTitle(data.get('iconUrl'),None)
        data['iconList']=getUrlList(urldata,data.get('iconUrl'))
        if len(data.get('iconList')) != 0:
            for u in url:
                b = write_to_file(u, 'c:/test/')
        else:
            pass
        #mongo data
    return b


def insertMongodbData(result):
    if getMongo()[MONGO_COLLECTION].insert(result):
        return 'true'
    else:
        print("mongo insert data fail" +result)
        return 'false'

def getIconUrl2(data):
    urldata= getTitle(data.get('iconUrl'), None)
    data['iconList'] = getUrlList(urldata, data.get('iconUrl'))
    if len(data.get('iconList')) != 0:
        url = data.get('iconList')
        for u in url:
           write_to_file(u, 'c:/test/')
    else:
        pass
    #mongo data
    b = insertMongodbData(data)
    return b

def main():
    try:
        param={
            'offset' : '0' ,
            'format' : 'json',
            'keyword' : '妹',
            'autoload' : 'true' ,
            'count' : str(INFO_COU) ,
            'cur_tab' : str(INFO_START),
            'from' : 'search_tab'
        }
        url = 'https://www.toutiao.com/search_content/'
        titles = getTitle(url,param)
        #print(getTitleData(titles))
        datas = [i for i in getTitleData(titles)]
        #print(data)
        #getIconUrl2(datas)
        #print([data for data in datas])
        pool = Pool()
        pool.map(getIconUrl2, [data for data in datas])
    #except Exception:
     #   print('main')
    finally:
        print('设计部合理，没有关浏览器')
if __name__ == '__main__':
    main()

