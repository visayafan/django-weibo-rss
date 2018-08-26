此项目为 [weibo-rss](https://github.com/zgq354/weibo-rss) 的Django实现版本。可以生成微博的rss订阅源。

Python版本为3.6，Django版本为2.1。其它需要安装的模块见requirements.txt。

> python manage.py runserver

运行起来后微博rss订阅链接为 `/weibo/{uid}`，例如 `http://127.0.0.1:8000/weibo/5997748429/`