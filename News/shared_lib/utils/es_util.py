# es_util.py

from datetime import datetime, timedelta

from elasticsearch import Elasticsearch, ElasticsearchException, NotFoundError
from elasticsearch.client.indices import IndicesClient
from elasticsearch_dsl import Search, Q
from elasticsearch_dsl.connections import connections

from News.shared_lib.config.constant import Config
from News.shared_lib.utils.time_util import TimeUtils
from News.shared_lib.utils.translate_util import translate_text


class ElasticsearchClient:
    def __init__(self):
        """
        初始化 Elasticsearch 客户端.
        """
        try:
            # 创建连接
            self.es = Elasticsearch(
                [{'host': Config.ES_HOST, 'port': Config.ES_PORT}],
                http_auth=(Config.ES_USERNAME, Config.ES_PASSWORD),
            )

            # 显式设置默认连接别名
            connections.create_connection(
                alias='default',
                hosts=[{'host': Config.ES_HOST, 'port': Config.ES_PORT}],
                http_auth=(Config.ES_USERNAME, Config.ES_PASSWORD)
            )

            if not self.es.ping():
                raise ValueError("连接 Elasticsearch 失败")

            # if not connections.get_connection().ping():
            #     raise ValueError("连接 Elasticsearch 失败")

            # 创建或检查索引
            self.create_or_check_index(Config.NEWS_INDEX)
        except ElasticsearchException as e:
            print("Elasticsearch 连接异常:", e)

    def create_or_check_index(self, index_name):
        """
        创建或检查指定的索引是否存在，并添加映射
        """
        indices_client = IndicesClient(self.es)

        # 定义映射和设置
        index_settings = {
            "settings": {
                "number_of_shards": 1,
                "number_of_replicas": 0
            },
            "mappings": {
                "properties": {
                    "title": {
                        "type": "text"
                    },
                    "link": {
                        "type": "keyword"
                    },
                    "content_cn": {
                        "type": "text"
                    },
                    "content_jp": {
                        "type": "text"
                    },
                    "category": {
                        "type": "keyword"
                    },
                    "pub_date": {
                        "type": "date",
                        "format": "yyyy年MM月dd日 HH:mm"
                    },
                    "get_date": {
                        "type": "date",
                        "format": "yyyy年MM月dd日 HH:mm"
                    }
                }
            }
        }

        if not indices_client.exists(index_name):
            indices_client.create(index=index_name, body=index_settings)
            print(f"索引 '{index_name}' 已创建。")
        else:
            # 更新现有索引的映射
            indices_client.put_mapping(index=index_name, body=index_settings['mappings'])

    # 查询分页新闻列表
    def search_news_list(self, category=None, page=1, per_page=10):
        """
        搜索新闻，支持分类、时间过滤和分页。
        首先根据抓取时间（get_date）筛选最近一小时的新闻，
        然后在这些新闻中按照发布时间（pub_date）进行排序
        :param category: 新闻类别。
        :param page: 页码。
        :param per_page: 每页新闻数量。
        :return: 搜索结果。
        """
        try:
            start_time, end_time = TimeUtils.get_past_hour_to_previous_day_time_range()

            search = Search(using=self.es, index="news")

            if category:
                print(f"Category filter applied: {category}")
                # 使用 category.keyword 进行精确匹配!!!
                # 这里注意下 es-py 不用上面那样, 直接 category 就行
                search = search.filter('term', **{"category": category})

            print(f"Start time: {start_time}, End time: {end_time}")
            # todo 需要打开
            search = search.filter('range', get_date={'gte': start_time, 'lte': end_time})
            # 按照发布时间（pub_date）进行降序排序
            search = search.sort('-pub_date')
            # 应用分页设置
            print(f"Page: {page}, Per page: {per_page}")
            search = search[(page - 1) * per_page: page * per_page]

            result = search.execute()

            # 获取总新闻条数
            total_hits = result.hits.total.value

            # 检查查询结果是否为空
            print(f"Total hits: {result.hits.total.value}")
            if result.hits.total.value == 0:
                return {"total": 0, "news": []}  # 返回空列表或其他指示没有匹配结果的数据结构
            else:
                news_list = [{'_id': hit.meta.id, **hit.to_dict()} for hit in result]
                return {"total": total_hits, "news": news_list}  # 返回新闻列表和总数
        except NotFoundError:
            return {"total": 0, "news": []}  # 返回空列表或其他指示没有匹配结果的数据结构

    # 根据去重条件查询新闻
    def search_specific_news(self, link, category):
        """
        根据新闻的标题和类别搜索特定新闻。
        :param link: 新闻链接。
        :param category: 新闻类别。
        :return: 搜索结果。
        """
        query = Q("bool", must=[Q("term", **{"link": link}), Q("term", **{"category": category})])
        search = Search(using=self.es, index="news").query(query)
        return search.execute()

    # 根据id查询新闻
    def get_news_by_id(self, news_id):
        """
        根据新闻的 ID 获取单条新闻。
        :param news_id: 新闻的唯一标识符。
        :return: 指定 ID 的新闻数据。
        """
        try:
            return self.es.get(index="news", id=news_id)
        except NotFoundError:
            return None

    # 分类别使用关键词搜索新闻(注意这里也需要分页)
    def search_news_by_keywords(self, keywords, category, page=1, per_page=10):
        """
        根据关键词和类别在指定时间范围内搜索新闻。
        :param keywords: 关键词列表。
        :param category: 新闻类别。
        :return: 搜索结果。
        """
        try:
            start_time, end_time = TimeUtils.get_past_hour_to_previous_day_time_range()

            # 构建查询条件
            query_conditions = []
            for word in keywords:
                # 添加中文内容和标题的短语匹配查询
                query_conditions.append(Q("match_phrase", content_cn=word))
                query_conditions.append(Q("match_phrase", title=word))

                # 添加日文内容的短语匹配查询
                translated_word = translate_text(word, "zh-CN", "ja")
                query_conditions.append(Q("match_phrase", content_jp=translated_word))

            # 组合查询条件
            query = Q('bool', must=[
                # todo 需要打开
                Q('range', get_date={'gte': start_time, 'lte': end_time}),
                Q('term', **{"category": category}),
                Q('bool', should=query_conditions, minimum_should_match=1)
            ])

            search = Search(using=self.es, index="news").query(query)
            search = search[(page - 1) * per_page: page * per_page]
            result = search.execute()

            news_list = [{'_id': hit.meta.id, **hit.to_dict()} for hit in result]
            return {"total": result.hits.total.value, "news": news_list}
        except ElasticsearchException as e:
            print("搜索异常:", e)
            return {"total": 0, "news": []}

    # 改用 es-py 去索引新闻
    def index_news_item(self, news_item, index_name):
        """
        将新闻项索引到 Elasticsearch 的指定索引中。
        :param news_item: 要索引的新闻项，应为一个包含新闻数据的字典。
        :param index_name: Elasticsearch 中的索引名。
        """
        # 如果 news_item 是对象且有 to_dict 方法，转换为字典
        if hasattr(news_item, 'to_dict'):
            news_item = news_item.to_dict()

        # 使用 index 方法将数据索引到 Elasticsearch
        response = self.es.index(index=index_name, body=news_item)

        # 打印响应信息（可选）
        print(response)

    # 更新指定新闻的获取日期（get_date）为当前时间
    def update_news_get_date(self, news_id):
        """
        更新指定新闻的获取日期（get_date）为当前时间。
        :param news_id: 新闻的唯一标识符。
        """
        updated_data = {
            "doc": {
                "get_date": TimeUtils.datetime_serializer(datetime.now())
            }
        }
        self.es.update(index="news", id=news_id, body=updated_data)

    def news_stati_by_day(self, category):
        search = Search(using=self.es, index="news").extra(size=0)
        date = datetime.today()
        search = search.filter('range', get_date={'gte': date.strftime('%Y年%m月%d日 00:00'),
                                                  'lt': (date + timedelta(days=1) - timedelta(minutes=1)).strftime(
                                                      '%Y年%m月%d日 %H:%M')})
        search = search.filter('term', category=category)  # 添加category过滤器
        search.aggs.bucket('publish_over_time', 'date_histogram', field='get_date', interval='hour')
        return search.execute()

    def news_stati_by_week(self, category):
        search = Search(using=self.es, index="news").extra(size=0)
        date = datetime.today()
        search = search.filter('range', get_date={'gte': (date - timedelta(days=6)).strftime('%Y年%m月%d日 00:00'),
                                                  'lt': (date + timedelta(days=1)).strftime('%Y年%m月%d日 00:00')})
        search = search.filter('term', category=category)  # 添加category过滤器
        search.aggs.bucket('publish_over_time', 'date_histogram', field='get_date', interval='1d')
        return search.execute()

    def news_stati_by_month(self, category):
        search = Search(using=self.es, index="news").extra(size=0)
        date = datetime.today()
        search = search.filter('range', get_date={'gte': (date - timedelta(days=29)).strftime('%Y年%m月%d日 00:00'),
                                                  'lt': (date + timedelta(days=1)).strftime('%Y年%m月%d日 00:00')})
        search = search.filter('term', category=category)  # 添加category过滤器
        search.aggs.bucket('publish_over_time', 'date_histogram', field='get_date', interval='1d')
        return search.execute()

    def get_latest_ten(self, category):
        # 创建一个Search对象
        search = Search(using=self.es, index="news").extra(size=10)

        # 添加一个过滤器，只选择特定类别的文档
        search = search.filter('term', category=category)

        # 按照get_date字段降序排序
        search = search.sort('-get_date')

        # 执行查询并返回结果
        return search.execute()

    def index_subs_item(self, subs_item):
        """
        将新闻项索引到 Elasticsearch 的指定索引中。
        :param subs_item: 要索引的订阅者信息，应为一个包含新闻数据的字典。
        """
        # 如果 news_item 是对象且有 to_dict 方法，转换为字典
        if hasattr(subs_item, 'to_dict'):
            subs_item = subs_item.to_dict()

        # 使用 index 方法将数据索引到 Elasticsearch
        self.es.index(index='subscribers', body=subs_item)

    def delete_subs_item(self, phone_number, news_category):
        """
        根据手机号和新闻类别从 Elasticsearch 的指定索引中删除文档。
        :param phone_number: 手机号。
        :param news_category: 新闻类别。
        """
        # 创建一个查询
        query = Q('bool', must=[Q('term', phone_number=phone_number), Q('term', category=news_category)])

        # 使用 delete_by_query 方法删除匹配的文档
        self.es.delete_by_query(index='subscribers', body={'query': query.to_dict()})

    def get_subs_grouped_data(self):
        # 创建一个Search对象
        search = Search(using=self.es, index='subscribers')

        # 添加聚合
        search.aggs.bucket('group_by_phone_number', 'terms', field='phone_number') \
            .bucket('group_by_category', 'terms', field='category')

        # 执行查询
        response = search.execute()

        # 创建一个空字典来存储结果
        result = {}

        # 遍历结果
        for phone_number_bucket in response.aggregations.group_by_phone_number.buckets:
            phone_number = phone_number_bucket.key
            result[phone_number] = []
            for category_bucket in phone_number_bucket.group_by_category.buckets:
                category = category_bucket.key
                result[phone_number].append(category)

        return result

    def search_for_subscriber(self, phone_number, category):
        # 创建一个Search对象
        search = Search(using=self.es, index='subscribers')

        # 添加查询条件
        search = search.query('term', phone_number=phone_number)
        search = search.query('term', category=category)

        # 执行查询并返回结果
        response = search.execute()

        return response
