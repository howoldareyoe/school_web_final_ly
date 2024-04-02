# news_fetcher.py
from datetime import datetime

import feedparser
import requests
from bs4 import BeautifulSoup

from News.shared_lib.config.constant import Config
from News.shared_lib.models.news import News
from News.shared_lib.utils.es_util import ElasticsearchClient
from News.shared_lib.utils.time_util import TimeUtils
from News.shared_lib.utils.translate_util import translate_text


# 存储新闻至ES
def fetch_and_store_news(categories):
    """
    获取指定类别的新闻并保存至 Elasticsearch。
    :param categories: 要抓取的新闻类别列表。
    """
    print("开始抓取新闻")
    es_client = ElasticsearchClient()

    try:
        for category in categories:
            if category not in Config.TOPICS:
                continue

            url_suffix = Config.TOPICS[category]
            print(f"正在抓取类别 '{category}' 的新闻")
            news_dict = get_news_dict(Config.BASE_URL + url_suffix, Config.ALL_NEWS)

            for idx, news in news_dict.items():
                print(f"处理新闻: {news['title']}")
                existing_news = es_client.search_specific_news(link=news['link'], category=category)
                if existing_news.hits.total.value > 0:
                    # 获取已存在新闻的 ID
                    existing_news_id = existing_news.hits[0].meta.id
                    # 更新该新闻的 get_date
                    es_client.update_news_get_date(existing_news_id)
                    continue

                print(f"爬取新闻内容: {news['link']}")
                news_content = get_news_content(news['link'])
                # 尝试翻译新闻内容
                translated_content = translate_text(news_content, 'ja', 'zh-cn')
                # print("翻译内容：", translated_content)

                news_item = News(
                    title=news_dict[idx]['title'],
                    link=news_dict[idx]['link'],
                    content_cn=translated_content,
                    content_jp=news_content,
                    category=category,
                    pub_date=TimeUtils.convert_to_beijing_time(news.get('pub_date')),
                    get_date=TimeUtils.datetime_serializer(datetime.now())
                )
                print("存储的pub_date：", TimeUtils.convert_to_beijing_time(news.get('pub_date')))
                print("存储的get_date：", TimeUtils.datetime_serializer(datetime.now()))

                print(f"正在将新闻 '{news['title']}' 索引到 Elasticsearch")
                es_client.index_news_item(news_item, Config.NEWS_INDEX)

        print("新闻抓取和存储完成。")
    except Exception as e:
        print(f"新闻抓取和存储过程中发生错误: {e}")


# 爬取指定主题(前十条或者所有)新闻的标题、链接、日期
# https://news.yahoo.co.jp/rss/categories/life.xml
def get_news_dict(url_suffix, news_type):
    """
    获取(前十条或者所有)新闻的标题、链接、日期
    :param url_suffix: 链接后缀
    :param news_type: 新闻类型（TOP_NEWS 或 ALL_NEWS）
    :return: 新闻信息字典
    """
    if news_type == Config.TOP_NEWS:
        rss_url = Config.BASE_URL + url_suffix
    else:
        rss_url = url_suffix
    feed = feedparser.parse(rss_url)

    news_dict = {}
    if news_type == Config.TOP_NEWS:
        for idx, item in enumerate(feed.entries, start=1):
            news_dict[idx] = {'title': item.title, 'link': item.link}
    elif news_type == Config.ALL_NEWS:
        for idx, item in enumerate(feed.entries, start=1):
            news_dict[idx] = {'title': item.title, 'link': item.link, "pub_date": item.published, "content": None}

    return news_dict


# 爬取指定链接的新闻内容
def get_news_content(base_url):
    """
    爬取指定链接对应的新闻内容
    :param base_url: 链接
    :return: 返回
    """
    page_number = 1
    all_content = []

    try:
        while True:
            url = f"{base_url}?page={page_number}"
            response = requests.get(url)

            if response.status_code != 200:
                break

            soup = BeautifulSoup(response.text, 'html.parser')
            content_div = soup.find('div', class_='article_body')

            if not content_div:
                break

            content = content_div.get_text()
            all_content.append(content)

            next_page_link = soup.find('a', rel='next')
            if not next_page_link:
                break

            page_number += 1

        return "\n".join(all_content)
    except requests.exceptions.RequestException as e:
        print("请求异常:", e)
