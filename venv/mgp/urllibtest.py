#encoding:utf-8
"""
@project = untitled2
@file = urllibtest
@author = Administrator
@create_time = 2018/4/9 10:55
"""
import urllib.request
import urllib.parse

data=bytes(urllib.parse.urlencode({'hello':'world'}),encoding='utf-8')
res = urllib.request.urlopen('http://www.baidu.com',data=data)
print(res.read().decode('utf-8'))
