import re

import requests
from bs4 import BeautifulSoup
from django.core.cache import cache
from django.http import JsonResponse
from django.views.decorators.cache import cache_page


# 此文件与生成微博rss订阅源无关，私用备份


# 大作手通知更新缓慢，设置24小时缓存，这样24小时内再次访问时直接返回缓存中的上次访问的rss/rss.xml，缓存到期后才再次执行函数体中的内容并更新缓存中的rss.xml
@cache_page(timeout=60 * 60 * 24)
def dazuoshou(request):
    feed = {
        'version': 'https://jsonfeed.org/version/1',
        'title': '大作手通知',
        'description': '大作手网站通知RSS',
        'home_page_url': 'http://www.dazuoshou.com.cn',
        'items': []
    }
    ann_link = 'http://www.dazuoshou.com.cn/ann/'
    lists = BeautifulSoup(requests.get(ann_link).content, 'html.parser').find_all('li', class_='clearfix')
    for x in lists:
        a = x.find('a')
        url = ann_link + a['href']
        if cache.get(url):
            feed['items'].append(cache.get(url))
        else:
            date = x.find('span').text
            title = date + ' ' + a.text
            b = BeautifulSoup(requests.get(url).content, 'html.parser')
            description = str(b.find('div', class_='content'))
            item = {
                'id': url,
                'url': url,
                'title': title,
                'content_html': description
            }
            cache.set(url, item)
            feed['items'].append(item)
    return JsonResponse(feed)


def fangeqiang(request):
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
    return JsonResponse(feed)


# 墙外楼去广告
def letscorp(request):
    letscorp_feed_url = 'http://feeds.feedburner.com/letscorp/aDmw?format=xml'
    b = BeautifulSoup(requests.get(letscorp_feed_url).content, 'xml')
    feed = {
        'version': 'https://jsonfeed.org/version/1',
        'title': b.rss.channel.title.string,
        'description': b.rss.channel.description.string,
        'home_page_url': b.rss.channel.link.string,
        'items': []
    }
    for item in b.find_all('item'):
        post_url = item.guid.string
        content = item.find('content:encoded').string
        # 去广告
        content = content[:content.find('<span>镜像链接：</span>')]
        # 段落缩进
        content = re.sub(r'<p>\u3000+', '<p style="text-indent:2em;">', content)
        feed['items'].append({
            'id': post_url,
            'title': item.title.string,
            'url': post_url,
            'content_html': content
        })
    return JsonResponse(feed)
