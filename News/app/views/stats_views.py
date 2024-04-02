from datetime import timedelta, datetime

from flask import Blueprint, request

from News.shared_lib.utils.es_util import ElasticsearchClient
from News.shared_lib.utils.response_util import response

stats_bp = Blueprint('stati', __name__)


# 测试
@stats_bp.route('/test', methods=['GET'])
def test():
    return "hhh"


@stats_bp.route('/', methods=['GET'])
def stati():
    stati_option = int(request.args.get('type'))
    category = request.args.get('category')
    if stati_option == 0:
        return stati_by_day(category)
    elif stati_option == 1:
        return stati_by_week(category)
    elif stati_option == 2:
        return stati_by_month(category)
    else:
        return response(code=500, message="查询失败，参数错误", data=None)


def stati_by_day(category):
    es_client = ElasticsearchClient()
    data = es_client.news_stati_by_day(category)
    data = data.aggregations.publish_over_time.buckets

    # 创建一个长度为24的列表，初始化为0
    doc_counts = [0] * 24

    # 遍历数据，更新对应小时的文档数量
    for item in data:
        # 提取小时数
        hour = int(item['key_as_string'][12:14])
        # 更新文档数量
        doc_counts[hour] = item['doc_count']

    res = {
        'day_counts': doc_counts
    }
    return response(code=200, message="成功获取日统计", data=res)


def stati_by_week(category):
    es_client = ElasticsearchClient()
    data = es_client.news_stati_by_week(category)
    data = data.aggregations.publish_over_time.buckets

    # 对数据按照'key_as_string'字段进行排序
    data.sort(key=lambda x: x['key_as_string'])

    print(data)
    # 获取数据中最晚的日期
    latest_date = datetime.strptime(data[-1]['key_as_string'], '%Y年%m月%d日 %H:%M')

    # 创建两个空列表
    dates = []
    doc_counts = []

    # 遍历过去7天的日期
    for i in range(7):
        # 计算当前日期
        date = (latest_date - timedelta(days=i)).strftime('%Y年%m月%d日')
        # 检查当前日期是否在数据中
        if any(item['key_as_string'].startswith(date) for item in data):
            # 如果在数据中，将对应的文档数量添加到对应的列表中
            dates.append(date)
            doc_counts.append(next(item['doc_count'] for item in data if item['key_as_string'].startswith(date)))
        else:
            # 如果不在数据中，将0添加到对应的列表中
            dates.append(date)
            doc_counts.append(0)

    res = {
        'dates': dates,
        'counts': doc_counts
    }
    return response(code=200, message="成功获取周统计", data=res)


def stati_by_month(category):
    es_client = ElasticsearchClient()
    data = es_client.news_stati_by_month(category)
    data = data.aggregations.publish_over_time.buckets

    # 对数据按照'key_as_string'字段进行排序
    data.sort(key=lambda x: x['key_as_string'])

    # 获取数据中最晚的日期
    latest_date = datetime.strptime(data[-1]['key_as_string'], '%Y年%m月%d日 %H:%M')

    # 创建两个空列表
    dates = []
    doc_counts = []

    # 遍历过去30天的日期
    for i in range(30):
        # 计算当前日期
        date = (latest_date - timedelta(days=i)).strftime('%Y年%m月%d日')
        # 检查当前日期是否在数据中
        if any(item['key_as_string'].startswith(date) for item in data):
            # 如果在数据中，将对应的文档数量添加到对应的列表中
            dates.append(date)
            doc_counts.append(next(item['doc_count'] for item in data if item['key_as_string'].startswith(date)))
        else:
            # 如果不在数据中，将0添加到对应的列表中
            dates.append(date)
            doc_counts.append(0)

    res = {
        'dates': dates,
        'counts': doc_counts
    }
    return response(code=200, message="成功获取月统计", data=res)
