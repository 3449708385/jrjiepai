#encoding:utf-8
"""
@project = untitled2
@file = requestsTest
@author = Administrator
@create_time = 2018/4/10 18:38
"""

import requests
import re

req=requests.get('https://blog.csdn.net/junbujianwpl/article/details/79411472')
#print(req.text)
result=re.findall('<label.*?>(.*?)</label>',req.text)
for r in result:
    #print(r)
    print(re.sub('<input.*?>','',r))