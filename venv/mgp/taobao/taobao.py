#encoding:utf-8
"""
@project = untitled2
@file = taobao
@author = Administrator
@create_time = 2018/4/11 22:38
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
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as Ec
from selenium.webdriver.support.ui import WebDriverWait
from pyquery import PyQuery as pq
from hashlib import md5
from mongoConf import *


def getDriver():
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    driver = webdriver.Chrome(chrome_options=chrome_options)
    #driver = webdriver.Chrome()
    return driver

def getJsChromeView(driver,url,text):
    try:
        driver.get(url)
        input = getWait(driver).until(Ec.presence_of_element_located((By.CSS_SELECTOR, '#q')))
        submit = getWait(driver).until(Ec.element_to_be_clickable((By.CSS_SELECTOR, '#J_TSearchForm > div.search-button > button')))
        input.send_keys(text)
        submit.click()
        total = getWait(driver).until(Ec.element_to_be_clickable((By.CSS_SELECTOR, '#mainsrp-pager > div > div > div > div.total')))
        return total.text
    except TimeoutException:
        print('timeout')
        getJsChromeView(driver,'https://www.taobao.com/','美食')


def next_page(driver, page):
    print(page)
    try:
        input = getWait(driver).until(Ec.presence_of_element_located((By.CSS_SELECTOR, '#mainsrp-pager > div > div > div > div.form > input')))
        submit = getWait(driver).until(Ec.element_to_be_clickable((By.CSS_SELECTOR, '#mainsrp-pager > div > div > div > div.form > span.btn.J_Submit')))
        input.clear()
        input.send_keys(page)
        submit.click()
        getWait(driver).until(Ec.text_to_be_present_in_element((By.CSS_SELECTOR, '#mainsrp-pager > div > div > div > ul > li.item.active > span'), str(page)))
    except TimeoutException:
        next_page(driver, page)

#wait 10 sec
def getWait(driver):
    return WebDriverWait(driver, 10)

def getMongo():
    client=pymongo.MongoClient(MONGO_URL)
    return client[MONGO_DB]

def insertMongodbData(result):
    if getMongo()[MONGO_COLLECTION].insert(result):
        return 'true'
    else:
        print("mongo insert data fail" +result)
        return 'false'


def getData(driver):
    getWait(driver).until(
        Ec.presence_of_element_located((By.CSS_SELECTOR, '#mainsrp-pager > div > div > div > ul > li.item.next > a > span:nth-child(1)')))
    html = driver.page_source
    doc = pq(html)
    datalist = doc('.m-itemlist .J_MouserOnverReq  ').items()
    #print(datalist[0])
    for item in datalist:
        #c=item.find('.pic .J_ItemPic')
        #print(item.find('.pic .J_ItemPic'))
        data = {
            'iconUrl':'http:'+item.find('.pic .J_ItemPic').attr('src'),
            'price':re.sub('\n','',item.find('.price').text()),
            'pyCount':item.find('.deal-cnt').text()[:-3],
            'title':re.sub('\n','',item.find('.J_ClickStat').text()),
            'titleUrl':item.find('.J_ClickStat').attr('href'),
            'anchor':item.find('.shopname').text(),
            'addr':item.find('.location').text()
        }
        print(data)
        #save mongo
        insertMongodbData(data)

def main():
    try:
        driver = getDriver()
        #print(getJsChromeView('https://www.taobao.com/', '美食'))
        total = getJsChromeView(driver, 'https://www.taobao.com/', '美食')
        for i in range(1, 100):
            next_page(driver, i)
            #解析数据
            getData(driver)
    #except Exception:
     #   print('main')
    finally:
        driver.close()

if __name__ == '__main__':
    main()