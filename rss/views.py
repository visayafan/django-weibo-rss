import re

import requests
from bs4 import BeautifulSoup
from django.core.cache import cache
from django.http import JsonResponse
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
TITLE_MAX_LENGTH = 20
# 微博缓存时间3天
STATUS_TTL = 60 * 60 * 24 * 3
# 避免频繁抓取微博，3小时更新一次
INDEX_TTL = 60 * 60 * 3


class FeedItem:
    def __init__(self, title, description, link):
        self.title = title
        self.description = description
        self.link = link


# 获取微博全文
def get_full_text(status):
    if 'isLongText' in status:
        long_status = requests.get(STATUS_DETAIL_API_URL.format(id=status['id'])).json()
        return long_status['data']['text']
    return status['text']


# 处理微博内容
def format_status(request, status):
    description = get_full_text(status)
    # 该条微博有转发别人微博
    if 'retweeted_status' in status:
        description += '<br/><br/>'
        retweeted_user = status['retweeted_status']['user']
        description += ('<div style="border-left: 3px solid gray; padding-left: 1em;">'
                        '转发<a href="{url}">@{name}</a>：{retweet}'
                        '</div>').format(url=retweeted_user['profile_url'],
                                         name=retweeted_user['screen_name'],
                                         retweet=format_status(request, status['retweeted_status']))
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


# 处理微博标题
def format_title(description):
    b = BeautifulSoup(description, 'html.parser')
    # 若微博内容文字少则直接做为标题
    if len(b.text.strip()) <= TITLE_MAX_LENGTH:
        return b.text
    # 否则取第1句的前TITLE_MAX_LENGTH个字符作为标题
    return re.split(r'[,.!?:;，。！？：；\s]', b.text.strip())[0][:TITLE_MAX_LENGTH] + '...'


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
                feed['items'].append(item)
                cache.set(status_id, item, STATUS_TTL)
            else:
                feed['items'].append(cache.get(status_id))
    return JsonResponse(feed)
