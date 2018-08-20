import requests
from bs4 import BeautifulSoup
from django.shortcuts import render

from weibo.models import FeedModel
from weibo.views import FeedItem


def dazuoshou(request):
    title = '大作手通知'
    description = '大作手网站通知RSS'
    link = 'http://www.dazuoshou.com.cn'
    profile = FeedModel(id=link, title=title, description=description, link=link)
    ann_link = 'http://www.dazuoshou.com.cn/ann/'
    lists = BeautifulSoup(requests.get(ann_link).content, 'html.parser').find_all('li', class_='clearfix')
    for x in reversed(lists):
        a = x.find('a')
        date = x.find('span').text
        title = date + ' ' + a.text
        link = ann_link + a['href']
        try:
            FeedModel.objects.get(id=link)
        except FeedModel.DoesNotExist:
            response = requests.get(link)
            b = BeautifulSoup(response.content, 'html.parser')
            description = ''.join(map(str, b.find('div', class_='content').contents))
            FeedModel.objects.create(id=link, title=title, link=link, description=description)
    feeds = FeedModel.objects.all()[:10]
    return render(request, 'weibo/atom.xml', {'profile': profile, 'items': feeds}, content_type='text/xml')


def fangeqiang(request):
    title = '翻个墙SSR更新通知'
    description = '翻个墙SSR更新通知'
    link = 'https://fangeqiang.com/408.html'
    profile = FeedItem(title, description, link)

    b = BeautifulSoup(requests.get(link).content, 'html.parser')
    all_a = b.find_all('a', class_='xButton')
    if all_a is not None:
        for a_a in all_a:
            if 'ssr' in a_a.text.lower():
                title = a_a.text.strip()
                break
    all_pre = b.find_all('pre', class_='prettyprint')
    if all_pre is not None:
        for a_pre in all_pre:
            if 'ssr://' in a_pre.text:
                urls = [x for x in a_pre.text.split() if 'ssr://' in x]
                description = '<a href="{ssrurl}">{ssrurl}</a><br/><br/><img src="{imgurl}"/>'.format(
                    ssrurl=urls[0], imgurl=urls[1])
                break
    items = [FeedItem(title, description, link)]
    return render(request, 'weibo/atom.xml', {'profile': profile, 'items': items}, content_type='text/xml')
