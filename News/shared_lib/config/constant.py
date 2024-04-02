class Config:
    # 新闻类型常量
    TOP_NEWS = "top_news"
    ALL_NEWS = "all_news"

    # 需要备份的新闻的 URL
    NEWS_URL = "https://news.yahoo.co.jp/rss/categories/life.xml"

    # 基本 URL 和主题名称与对应的 RSS URL
    BASE_URL = "https://news.yahoo.co.jp/rss/categories/"
    TOPICS = {
        "主要": "life.xml",
        "国内": "domestic.xml",
        "国际": "world.xml",
        "経済": "business.xml",
        "エンタメ": "entertainment.xml",
        "スポーツ": "sports.xml",
        "IT": "it.xml",
        "科学": "science.xml"
    }

    # 序号、标题和对应的 URL
    # TOPIC_MAPPING = {idx: (topic, BASE_URL + TOPICS[topic]) for idx, topic in enumerate(TOPICS, start=1)}

    # 主题数量
    # TOPIC_COUNT = len(TOPICS)

    # 更新间隔、新闻数量限制等
    UPDATE_INTERVAL = 900  # 更新间隔，单位为秒（10分钟）
    MAX_NEWS_COUNT = 20  # 最大新闻数量
    MIN_NEWS_COUNT = 5  # 最小新闻数量

    # 翻译或摘要相关
    SUMMARY_PROMPT = "请将下面的内容归纳成30个字之内的短句："  # 传递给 AI 的前置句子

    # 请求头设置
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko'
    }

    # Elasticsearch 配置
    ES_HOST = 'x.x.x.x'
    ES_PORT = 9200
    ES_USERNAME = 'xxxxx'
    ES_PASSWORD = 'xxxx'

    NEWS_INDEX = 'xxxxx'
    PER_PAGE = 10
