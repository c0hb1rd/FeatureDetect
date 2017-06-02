# -*- coding: utf-8 -*-
import requests
import re
import json
from bs4 import BeautifulSoup

domain = 'https://www.duitang.com'

headers = {
    'Accept':'text/plain, */*; q=0.01',
    'Accept-Encoding':'gzip, deflate, sdch',
    'Accept-Language':'zh-CN,zh;q=0.8,en;q=0.6',
    'Connection':'keep-alive',
    'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
    'X-Requested-With':'XMLHttpRequest'
}

urlList = []


def getImageUrl(urls):
    for url in urls:
        ret = requests.get(url, headers=headers).text
        html = BeautifulSoup(ret, "lxml")
        img = html.find("img", attrs={'class': 'js-favorite-blogimg'})
        url = img.attrs.get("src", 0)
        if url != 0:
            with open("imgUrl.txt", "a+") as f: f.write(url + "\n")


def getUrl(url):
    ret = requests.get(url, headers=headers).text
    html = BeautifulSoup(ret, "lxml")
    img = html.find("img", attrs={'class': 'js-favorite-blogimg'})
    nt = html.find("a", attrs={'class': 'shownext'})
    if nt:
        ntUrl = domain + nt.attrs.get("href")
        with open("url.txt", "a+") as f: f.write(ntUrl + "\n")
        getUrl(ntUrl)
    else:
        return

def downloadImg(urls):
    count = 0
    for url in urls:
        ret = requests.get(url, stream=True, headers=headers).content
        with open("user%d.jpg" % count, "wb+") as f: f.write(ret)
        count += 1


with open("imgUrl.txt", "r") as f:
    for line in f.readlines():
        urlList.append(line[:-1])

downloadImg(list(set(urlList)))
# count = 0
# for url in urlList:
#     ret = requests.get(url, stream=True, headers=headers)
#     with open("user%d.jpg" % count, "w+") as f: f.write(ret.text)
#     count += 1
