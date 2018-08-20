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


def format_status(request, status):
    description = get_full_text(status)
    # 该条微博有转发别人微博
    if 'retweeted_status' in status:
        description += '<br/><br/>'
        retweeted_user = status['retweeted_status']['user']
        description += '<div style="border-left: 3px solid gray; padding-left: 1em;">转发<a href="{url}">@{name}</a>：{retweet}</div>'.format(
            url=retweeted_user['profile_url'],
            name=retweeted_user['screen_name'], retweet=format_status(request, status['retweeted_status']))
    # 处理表情图标，默认表情图标全部转成文字
    b = BeautifulSoup(description, 'html.parser')
    if not request.GET.get('emoji'):
        icons = b.find_all('span', class_='url-icon')
        # 去掉位置/链接前的图标，太大太难看
        if icons is not None:
            for icon in icons:
                # 表情图标img标签的alt值类似"[哈哈]"
                if icon.img.has_attr('alt') and ('[' in icon.img.get('alt')):
                    icon.replace_with(icon.img.get('alt'))
                # 不是表情图标直接删除，例如文章链接、地理位置前的图标
                else:
                    icon.decompose()
    description = str(b)
    # 后跟所有图片
    if 'pics' in status:
        for pic in status['pics']:
            # 默认显示小图，点击可打开大图
            description += '<br/><br/><a href="{large_url}" target="_blank"><img src="{small_url}"/></a>'.format(
                large_url=pic['large']['url'], small_url=pic['url'])
    return description


def format_title(description):
    b = BeautifulSoup(description, 'html.parser')
    # 若微博内容文字少则直接做为标题
    if len(b.text) <= TITLE_MAX_LENGTH:
        return b.text
    # 否则取第1句的前TITLE_MAX_LENGTH个字符作为标题
    return re.split(r'[,.!?:;，。！？：；]', b.text)[0][:TITLE_MAX_LENGTH] + '...'


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
            item.description = format_status(request, status)
            item.link = 'https://m.weibo.cn/status/{id}'.format(id=status['id'])
            item.title = format_title(item.description)
            items.append(item)

    return render(request, 'weibo/atom.xml', {'profile': profile, 'items': items}, content_type='text/xml')
