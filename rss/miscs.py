import requests
from bs4 import BeautifulSoup
from django.core.cache import cache
from django.shortcuts import render
from django.views.decorators.cache import cache_page
from rest_framework.response import Response
from rest_framework.views import APIView

from .views import FeedItem


# 此文件与生成微博rss订阅源无关，私用备份


# 大作手通知更新缓慢，设置24小时缓存，这样24小时内再次访问时直接返回缓存中的上次访问的rss/rss.xml，缓存到期后才再次执行函数体中的内容并更新缓存中的rss.xml
@cache_page(timeout=60 * 60 * 24)
def dazuoshou(request):
    title = '大作手通知'
    description = '大作手网站通知RSS'
    link = 'http://www.dazuoshou.com.cn'
    profile = FeedItem(title, description, link)
    ann_link = 'http://www.dazuoshou.com.cn/ann/'
    lists = BeautifulSoup(requests.get(ann_link).content, 'html.parser').find_all('li', class_='clearfix')
    items = []
    for x in lists:
        a = x.find('a')
        link = ann_link + a['href']
        if cache.get(link):
            items.append(cache.get(link))
        else:
            date = x.find('span').text
            title = date + ' ' + a.text
            response = requests.get(link)
            b = BeautifulSoup(response.content, 'html.parser')
            description = ''.join(map(str, b.find('div', class_='content').contents))
            item = FeedItem(title, description, link)
            cache.set(link, item)
            items.append(item)
    return render(request, 'rss/rss.xml', {'profile': profile, 'items': items}, content_type='text/xml')


class FanGeQiang(APIView):
    def get(self, request):
        # feedjson标准 https://jsonfeed.org/version/1
        feed = {
            'version': 'https://jsonfeed.org/version/1',
            'title': '翻个墙SSR更新通知',
            'description': '翻个墙SSR更新通知',
            'home_page_url': 'https://fangeqiang.com/408.html',
            'items': []
        }
        b = BeautifulSoup(requests.get(feed['home_page_url']).content, 'html.parser')
        controls = b.find_all('div', class_='xControl')
        if controls:
            for c in controls:
                if 'ssr' in c.a.text.lower():
                    pt = c.find_next('pre', class_='prettyprint')
                    urls = [x for x in pt.text.split() if 'ssr://' in x]
                    description = '<a href="{ssrurl}">{ssrurl}</a><br/><br/><img src="{imgurl}"/>'.format(ssrurl=urls[0], imgurl=urls[1])
                    title = c.a.text.strip()
                    feed['items'].append({
                        'id': title,
                        'title': title,
                        'content_html': description
                    })
        return Response(feed)
