import requests
import json
import logging
from bs4 import BeautifulSoup
from selenium import webdriver
logger = logging.getLogger('django')

headers = {
    'Request URL': 'https://www.cwb.gov.tw/Data/js/WeatherIcon.js?_=1673188882513',
    'Request Method': 'GET',
    'Status Code': '200',
    'Remote Address': '[2001:b000:583::6]:443',
    'Referrer Policy': 'strict-origin-when-cross-origin',
    'content-encoding': 'br',
    'content-type': 'application/javascript',
    'date': 'Sun, 08 Jan 2023 14:41:22 GMT',
    'last-modified': 'Tue, 20 Aug 2019 03:25:27 GMT',
    'server': 'HiNetCDN/2211',
    'vary': 'Accept-Encoding',
    'x-cache': 'MISS, EXPIRED, EXPIRED',
    'x-request-id': '29dcf70f6315b8cd43b79dcf97072542',
    'authority': 'www.cwb.gov.tw',
    'method': 'GET',
    'path': '/Data/js/WeatherIcon.js?_=1673188882513',
    'scheme': 'https',
    'accept': 'text/javascript, application/javascript, application/ecmascript, application/x-ecmascript, */*; q=0.01',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7,zh-CN;q=0.6',
    'cookie': 'V8_LANG=C; _gid=GA1.3.859957612.1673110833; _ga_2R6TQPFZN4=GS1.1.1673182803.1.0.1673182803.0.0.0; FontSize=fsNormal; V8_CID_COUNTY=63; _gat_UA-126485471-6=1; _gat_UA-126485471-1=1; _ga=GA1.1.609151595.1673110833; TS010c55bd=0107dddfef9e450fdfc7e2c15b6061014351664103b2f47f37b2bbe15aecc3918697dc1aa5fb7923c72f9870552ce09f938ed3c3c0; _ga_K6HENP0XVS=GS1.1.1673185886.5.1.1673188882.55.0.0',
    'referer': 'https://www.cwb.gov.tw/V8/C/K/Weather_Icon.html',

    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
    'x-requested-with': 'XMLHttpRequest'
}


response = requests.get(
    "https://www.cwb.gov.tw/V8/C/K/Weather_Icon.html", headers=headers)

print(response.text)
