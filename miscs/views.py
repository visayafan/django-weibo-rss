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
    return render(request, 'weibo/atom.xml', {'profile': profile, 'items': items}, content_type='text/xml')


def fangeqiang(request):
    profile = FeedItem()
    profile.title = '翻个墙SSR更新通知'
    profile.description = '翻个墙SSR更新通知'
    profile.link = 'https://fangeqiang.com/408.html'
    b = BeautifulSoup(requests.get(profile.link), 'html.parser')
    item = FeedItem()
    all_a = b.find_all('a', class_='xButton')
    if all_a is not None:
        for a_a in all_a:
            if 'ssr' in a_a.text.lower():
                item.title = a_a.text.strip()
                break
    all_pre = b.find_all('pre', class_='prettyprint')
    if all_pre is not None:
        for a_pre in all_pre:
            if 'ssr://' in a_pre.text:
                item.description = a_pre.text
                break
    item.link = profile.link
    items = [item]
    return render(request, 'weibo/atom.xml', {'profile': profile, 'items': items}, content_type='text/xml')
