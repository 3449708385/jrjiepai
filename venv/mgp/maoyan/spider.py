#encoding:utf-8
"""
@project = untitled2
@file = spider
@author = Administrator
@create_time = 2018/4/11 10:16
"""
import requests
import re
from requests.exceptions import RequestException
import json
import time
from multiprocessing import Pool  #进程池，不是线程池

def getUrlSource(urltemp):
    try:
        headers={"User-Agent":"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36"}
        resp=requests.get(urltemp,headers=headers)
        if resp.status_code==200:
            return resp.text
        return None
    except RequestException:
        return None

def getPattern(text):
    pattern=re.compile('<dd.*?data-src="(.*?)" alt.*?>.*?<p.*?><a.*?>(.*?)</a>.*?releasetime">(.*?)</p>.*?integer">(.*?)</i>.*?fraction">(.*?)</i>',re.S)
    items=re.findall(pattern,text)
    for item in items:
        yield {
            'iconUrl': item[0],
            'title': item[1],
            'createTime': time.time(),
            'updateTime': time.time(),
            'time': item[2].strip()[5:],
            'sc': item[3] + item[4]
        }
    return items

def write_to_file(file,text):
    with open(file,'a',encoding='utf-8') as f:    #中文存储转码
        f.write(json.dumps(text,ensure_ascii=False)+'\n')
        f.close()

def main(offset):
    sourcefile=getUrlSource('http://maoyan.com/board/4?offset='+str(offset))
    #print(sourcefile)
    if sourcefile!=None:
        #print(sourcefile)
        items=getPattern(sourcefile)
        for item in items:
           print(item)
           write_to_file('C:/text.txt',item)
            #print(item[0],item[1],item[2],item[3]+item[4])

    else:
        print(sourcefile)

if __name__ == '__main__':
    #for i in range(10):
     #   main(i*10)
    pool = Pool()
    pool.map(main,[i*10 for i in range(0,10)])