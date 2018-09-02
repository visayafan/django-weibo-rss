import json
import logging
import os
import re
from functools import lru_cache
from json import JSONDecodeError

import requests
import wget
from PIL import Image
from bs4 import BeautifulSoup
from django.conf import settings
from django.core.cache import cache
from django.http import JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.cache import cache_page

WEIBO_API_ROOT = 'https://m.weibo.cn/'
# 以下{uid}表用户id，{id}表某条微博id
# 全部微博列表
WEIBO_LIST_API_URL = WEIBO_API_ROOT + 'api/container/getIndex?containerid=230413{uid}_-_WEIBO_SECOND_PROFILE_WEIBO&page={page_num}'
# 用户详情
PEOPLE_DETAIL_API_URL = WEIBO_API_ROOT + 'api/container/getIndex?type=uid&value={uid}'
# 单条微博全文
STATUS_DETAIL_API_URL = WEIBO_API_ROOT + 'statuses/show?id={id}'
# 用户微博首页
PEOPLE_WEIBO_HOME_URL = WEIBO_API_ROOT + '{uid}'
# 微博全文
PEOPLE_WEIBO_FULLTEXT_URL = WEIBO_API_ROOT + 'status/{id}'
# 最大标题长度
TITLE_MAX_LENGTH = 30
# 微博缓存时间3天
STATUS_TTL = 60 * 60 * 24 * 3
# 避免频繁抓取微博，3小时更新一次
INDEX_TTL = 60 * 60 * 3

mark = 0
left_border = '<div style="border-left: 3px solid gray; padding-left: 1em;">{}</div>'
# 保存emoji图片的目录，app中static中的images目录
emoji_dir_base = 'weibo/static/'
emoji_url_dir = 'images'
emoji_dir = os.path.join(emoji_dir_base, emoji_url_dir)

logging.basicConfig(level=logging.INFO)


# 获取微博全文
def get_full_text(status):
    if 'isLongText' in status and status['isLongText']:
        # 有些微博无法查看全文
        try:
            long_status = requests.get(STATUS_DETAIL_API_URL.format(id=status['id'])).json()
            return long_status['data']['text']
        except JSONDecodeError:
            logging.warning('查看全文失败：' + STATUS_DETAIL_API_URL.format(id=status['id']))
    return status['text']


# TODO 等微博所有表情图标全部下载到本地后将所有图标列在一个列表里，目前先用缓存的方法
@lru_cache(maxsize=1)
def get_emoji_by_listdir(emoji_dir, mark):
    return os.listdir(emoji_dir)


# 表情图标用已经处理过的小图标
def format_emoji_resize(request, description, emoji_size):
    global mark
    b = BeautifulSoup(description, 'html.parser')
    emojis_tag = b.find_all('span', class_='url-icon')
    if emojis_tag:
        for emoji_tag in emojis_tag:
            url = emoji_tag.img.get('src')
            emoji_name = url.split('/')[-1]
            os.makedirs(emoji_dir, exist_ok=True)
            emoji_dir_full_path = os.path.join(emoji_dir, emoji_name)
            if emoji_name not in get_emoji_by_listdir(emoji_dir, mark):
                if url.startswith('//'):
                    url = 'http:' + url
                logging.info('正在下载emoji:' + url)
                wget.download(url, emoji_dir_full_path)
                Image.open(emoji_dir_full_path).resize(emoji_size).save(emoji_dir_full_path)
                mark += 1
            # 应该在nginx中加上 proxy_set_header Host $host:$server_port;
            # 详见 https://www.jianshu.com/p/cc5167032525
            emoji_tag.img['src'] = 'http://' + '/'.join([get_domain_name_or_host_ip(request), settings.STATIC_URL.replace('/', ''), emoji_url_dir, emoji_name])
    return b


# 处理微博内容
def format_status(request, status):
    description = get_full_text(status)
    # 该条微博有转发别人微博
    if 'retweeted_status' in status:
        description += '<br/><br/>'
        retweeted_user = status['retweeted_status']['user']
        description += left_border.format(
            '@<a href="{url}">{name}</a>：{retweet}'.format(
                url=retweeted_user['profile_url'],
                name=retweeted_user['screen_name'],
                retweet=format_status(request, status['retweeted_status'])))
    # emoji裁剪后的大小
    emoji_size = (17, 17)
    b = format_emoji_resize(request, description, emoji_size)
    description = str(b)
    # 后跟所有图片
    if 'pics' in status:
        for pic in status['pics']:
            # 默认显示小图，点击可打开大图
            description += '<br/><br/><a href="{large_url}"><img src="{small_url}"/></a>'.format(
                large_url=pic['large']['url'], small_url=pic['url'])
    return description


# 处理微博标题
def format_title(description):
    b = BeautifulSoup(description, 'html.parser')
    # 去除掉HTML标签
    cleaned_des = b.text.strip()
    # 若微博正文中含有【】则将其包含内容作为标题
    rst = re.search(r'【(.*?)】', cleaned_des)
    if rst:
        cleaned_des = rst.group(1)
    # 若微博内容文字少则直接做为标题
    if len(cleaned_des) <= TITLE_MAX_LENGTH:
        return cleaned_des
    # 否则取第1句的前TITLE_MAX_LENGTH个字符作为标题
    title = cleaned_des[:TITLE_MAX_LENGTH]
    sear = re.search(r'[,.!?;，。！？；]', title[::-1])
    if sear:
        title = title[:-sear.end()]
    return title


def filter_status(request, items):
    exs_list = []
    ins_list = []
    try:
        with open('filter.json', encoding='utf-8') as file:
            fg = json.load(file)
            exs_list = fg['exclude']
            ins_list = fg['include']
    except IOError:
        pass

    # exclude=a|b|c，若微博内容包含a,b,c中任何一个则过滤掉
    exs = request.GET.get('exclude')
    if exs:
        exs_list.extend(exs.split('|'))
    if exs_list:
        items = [item for item in items if not any(ex in item['content_html'] for ex in exs_list)]
    # include=a|b|c，当微博内容包含a,b,c中任意一个时才保留，否则过滤
    ins = request.GET.get('include')
    if ins:
        ins_list.extend(ins.split('|'))
    if ins_list:
        items = [item for item in items if any(i in item['content_html'] for i in ins_list)]
    return items


@cache_page(timeout=INDEX_TTL)
def index(request, uid):
    p = requests.get(PEOPLE_DETAIL_API_URL.format(uid=uid)).json()['data']['userInfo']
    # feedjson标准 https://jsonfeed.org/version/1
    feed = {
        'version': 'https://jsonfeed.org/version/1',
        'title': '{name}的微博'.format(name=p['screen_name']),
        'description': p['description'],
        'home_page_url': PEOPLE_WEIBO_HOME_URL.format(uid=uid),
        'items': []
    }
    # 获取用户最近的微博
    weibo_response = requests.get(WEIBO_LIST_API_URL.format(uid=uid, page_num=1)).json()
    items = []
    for card in weibo_response['data']['cards']:
        if 'mblog' in card:
            status = card['mblog']
            status_id = status['id']
            if not cache.get(status_id):
                description = format_status(request, status)
                url = PEOPLE_WEIBO_FULLTEXT_URL.format(id=status_id)
                title = format_title(description)
                item = {
                    'id': url,
                    'url': url,
                    'title': title,
                    'content_html': description
                }
                items.append(item)
                cache.set(status_id, item, STATUS_TTL)
            else:
                items.append(cache.get(status_id))
    feed['items'] = filter_status(request, items)
    return JsonResponse(feed)


def home(request):
    url = None
    origin_url = None
    if request.method == 'POST':
        # 移动端访问时若访问地址为域名访问则会跳转到ID访问，例如https://weibo.com/rmrb会跳转到https://m.weibo.cn/u/2803301701，跳转后链接在r.url中
        origin_url = request.POST.get('url')
        r = requests.get(origin_url, headers={'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit'})
        uid = r.url.split('/')[-1]
        uid = re.match(r'\d+', uid).group(0)
        url = request.build_absolute_uri(reverse('weibo', args=[uid]))
    return render(request, 'weibo/home.html', {'url': url, 'origin_url': origin_url})
