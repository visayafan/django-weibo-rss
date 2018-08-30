import re

import requests
import rfc3339
from bs4 import BeautifulSoup
from dateutil import parser
from django.core.cache import cache
from django.http import JsonResponse, HttpResponse
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
@cache_page(timeout=60 * 60 * 3)
def letscorp(request):
    letscorp_feed_url = 'http://feeds.feedburner.com/letscorp/aDmw?format=xml'
    b = BeautifulSoup(requests.get(letscorp_feed_url).content, 'xml')
    feed = {
        'version': 'https://jsonfeed.org/version/1',
        'title': b.rss.channel.title.text,
        'description': b.rss.channel.description.text,
        'home_page_url': b.rss.channel.link.text,
        'items': []
    }
    for item in b.find_all('item'):
        post_url = item.guid.text
        post_title = item.title.text
        post_date = rfc3339.rfc3339(parser.parse(item.pubDate.text))
        dit = {
            'id': post_url,
            'title': post_title,
            'url': post_url,
            'date_published': post_date
        }
        if not cache.get(post_url):
            content = item.find('content:encoded').text
            # 去广告
            ad1 = content.find('<span>镜像链接：</span>')
            if ad1 != -1:
                content = content[:ad1]
            bs = BeautifulSoup(content, 'html.parser')

            # 所有在href属性包含在ads_href_list的超链接会被删掉
            ads_href_list = ['amazon.com/gp',
                             'chrome.google.com/webstore']
            all_ads_link = bs.find_all(lambda tag: tag.name == 'a' and (tag.has_attr('href') and any(x for x in ads_href_list if x in tag.get('href'))))
            if all_ads_link:
                for link in all_ads_link:
                    link.decompose()

            # 删除分享图片
            feedflare = bs.find('div', class_='feedflare')
            if feedflare:
                feedflare.decompose()

            # 删除广告图片
            ads_keywords = ['letscorp/aDmw']
            ads_images = bs.find_all(lambda tag: tag.name == 'img' and (tag.has_attr('src') and any(x for x in ads_keywords if x in tag.get('src'))))
            if ads_images:
                for image in ads_images:
                    image.decompose()

            # 删除相关日志
            rpt = bs.find('h2', class_='related_post_title')
            if rpt:
                rpt.decompose()
            rp = bs.find('ul', class_='related_post')
            if rp:
                rp.decompose()
            # 换行变分段
            content = content.replace('<br />', '</p><p>')
            # 段落缩进
            content = re.sub(r'<p>(\n)?\u3000*', '<p>\u3000\u3000', content)
            content = str(bs)
            dit['content_html'] = content
            feed['items'].append(dit)
            cache.set(post_url, content)
        else:
            dit['content_html'] = cache.get(post_url)
            feed['items'].append(dit)
    return JsonResponse(feed)


# 联合早报，用了feedx.net的订阅源
@cache_page(timeout=60 * 60 * 12)
def zaobaotoday(request):
    zaobao_feed_url = 'https://feedx.net/rss/zaobaotoday.xml'
    b = BeautifulSoup(requests.get(zaobao_feed_url).content, 'xml')
    item_list = []
    for item in b.find_all('item'):
        if item.title.text not in item_list:
            item_list.append(item.title.text)
            # 段落缩进
            dt = item.description.text.replace('<p>', '<p>\u3000\u3000')
            # 去掉广告及推荐
            pos = dt.find('<div class="tagcloud">')
            if pos != -1:
                dt = dt[:pos]
            item.description.string.replace_with(dt)
        else:
            item.extract()
    return HttpResponse(str(b), content_type='application/xml')
