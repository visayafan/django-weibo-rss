此项目为 [weibo-rss](https://github.com/zgq354/weibo-rss) 的Django实现版本，可以生成微博的rss订阅源。

## 依赖

Python版本为3.6，Django版本为2.1。

依赖模块可以用命令 `pip install -r requirements.txt` 来安装。

## 运行

运行命令为 `python manage.py runserver`， 运行成功后访问 `http://127.0.0.1:8000`可打开首页，首页提供了通过微博链接得到微博订阅源的方法。

## 过滤

有两种过滤方法：

- 全局过滤：在filter.json中添加过滤关键字，将对所有微博实现过滤：包含exclude列表中关键字的微博和不包含include列表中关键字的微博将被过滤掉；
- 局部过滤：可通过URL查询参数方法实现对某个博主的微博进行过滤，方法为/?exclude=广告|红包&include=Python|Java，多个关键字以`|`分隔；

## Demo

我在heroku上建了个Demo，链接为 [https://django-weibo-rss.herokuapp.com](https://django-weibo-rss.herokuapp.com)，因为heroku每月有时长限制，所以每月最后几天可能不能使用。

