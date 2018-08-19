import re

import requests
from bs4 import BeautifulSoup
from django.shortcuts import render

WEIBO_API_ROOT = 'https://m.weibo.cn/'
# 全部微博列表
WEIBO_LIST_URL = WEIBO_API_ROOT + 'api/container/getIndex?containerid=230413{id}_-_WEIBO_SECOND_PROFILE_WEIBO&page={page_num}'
# 用户详情
PEOPLE_DETAIL_URL = WEIBO_API_ROOT + 'api/container/getIndex?type=uid&value={id}'

# 单条微博全文
STATUS_DETAIL_URL = WEIBO_API_ROOT + 'statuses/show?id={id}'

# 最大标题长度
TITLE_MAX_LENGTH = 20


class FeedItem():
    title = ''
    description = ''
    link = ''


# 获取微博全文
def get_full_text(status):
    if 'isLongText' in status:
        long_status = requests.get(STATUS_DETAIL_URL.format(id=status['id'])).json()
        return long_status['data']['text']
    return status['text']


def format_status(status):
    text = get_full_text(status)
    # 该条微博有转发别人微博
    if 'retweeted_status' in status:
        text += '<br/><br/>'
        retweeted_user = status['retweeted_status']['user']
        text += '<div style="border-left: 3px solid gray; padding-left: 1em;">转发<a href="{url}">@{name}</a>：{retweet}</div>'.format(
            url=retweeted_user['profile_url'],
            name=retweeted_user['screen_name'], retweet=format_status(status['retweeted_status']))
    # 后跟所有图片
    if 'pics' in status:
        for pic in status['pics']:
            text += '<br/><br/><a href="{large_url}" target="_blank"><img src="{small_url}"/></a>'.format(
                large_url=pic['large']['url'], small_url=pic['url'])
    b = BeautifulSoup(text, 'html.parser')
    icons = b.find_all('span', class_='url-icon')
    # 去掉位置前的图标，太大太难看
    if icons is not None:
        for icon in icons:
            if 'location' in icon.img['src']:
                icon.decompose()
    return str(b)


def format_title(description):
    b = BeautifulSoup(description, 'html.parser')
    # 若第1句少于TITLE_MAX_LENGTH个字符则取第1句话作为标题
    title = re.split(',|\.|\!|\?|，|。|！|？', b.get_text())[0][:TITLE_MAX_LENGTH] + '...'
    return title


def index(request, uid):
    profile = FeedItem()
    # 首先根据uid获取用户信息
    profile_response = requests.get(PEOPLE_DETAIL_URL.format(id=uid)).json()
    p = profile_response['data']['userInfo']
    profile.title = '{name}的微博'.format(name=p['screen_name'])
    profile.description = p['description']
    profile.link = 'https://weibo.com/{id}'.format(id=uid)

    # 获取用户最近的微博
    items = []
    weibo_response = requests.get(WEIBO_LIST_URL.format(id=uid, page_num=1)).json()
    for card in weibo_response['data']['cards']:
        if 'mblog' in card:
            item = FeedItem()
            status = card['mblog']
            item.description = format_status(status)
            item.link = 'https://m.weibo.cn/status/{id}'.format(id=status['id'])
            item.title = format_title(item.description)
            items.append(item)

    return render(request, 'weibo/atom.xml', {'profile': profile, 'items': items}, content_type='text/xml')
