import requests
from bs4 import BeautifulSoup
from django.shortcuts import render

from weibo.views import FeedItem


def dazuoshou(request):
    profile = FeedItem()
    profile.title = '大作手通知'
    profile.description = '大作手网站通知RSS'
    profile.link = 'http://www.dazuoshou.com.cn'
    dzsurl = 'http://www.dazuoshou.com.cn/ann/'
    lists = BeautifulSoup(requests.get(dzsurl).content, 'html.parser').find_all('li', class_='clearfix')
    items = []
    for x in lists:
        item = FeedItem()
        a = x.find('a')
        date = x.find('span').text
        item.title = date + ' ' + a.text
        item.link = dzsurl + a['href']
        item.description = ''.join(map(str, BeautifulSoup(requests.get(item.link).content, 'html.parser').find('div', class_='content').contents))
        items.append(item)
    return render(request, 'miscs/dazuoshou.xml', {'profile': profile, 'items': items}, content_type='text/xml')
