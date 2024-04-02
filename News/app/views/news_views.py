from flask import Blueprint, request

from News.shared_lib.utils.es_util import ElasticsearchClient
from News.shared_lib.utils.response_util import response
from News.shared_lib.config.constant import Config

news_bp = Blueprint('news', __name__)


# 测试
@news_bp.route('/', methods=['GET'])
def test():
    return "hhh"


# 查询所需类别的最新分页新闻列表
@news_bp.route('/list', methods=['POST'])
def get_news():
    data = request.json  # 获取JSON格式的请求体数据
    category = data.get('category', None)
    page = int(data.get('page', 1))

    es_client = ElasticsearchClient()
    search_result = es_client.search_news_list(category=category, page=page, per_page=Config.PER_PAGE)

    # 使用字典访问方式
    if 'news' in search_result and 'total' in search_result:
        # 从每个 hit 中提取指定的字段
        news_list = [
            {
                'id': hit['_id'],
                'title': hit['title'],
                'link': hit['link'],
                'pub_date': hit['pub_date'],
                'category': hit['category']
            } for hit in search_result['news']
        ]
        total_hits = search_result['total']
    else:
        # 如果 search_result 的格式不正确，则返回空列表和总数为0
        news_list = []
        total_hits = 0

    result_data = {
        'total': total_hits,
        'news': news_list
    }

    return response(code=200, message="成功获取新闻列表", data=result_data)


# 根据id查询新闻详情
@news_bp.route('/detail', methods=['GET'])
def get_news_detail():
    news_id = request.args.get('id')
    if not news_id:
        return response(code=400, message="缺少新闻ID", data=None)

    es_client = ElasticsearchClient()

    # 调用 Elasticsearch 客户端以获取新闻详情
    news_detail = es_client.get_news_by_id(news_id)

    # 检查是否找到了新闻
    if news_detail:
        news_source = news_detail['_source']
        # 提取新闻详情信息
        news_data = {
            'id': news_detail['_id'],
            'title': news_source.get('title'),
            'link': news_source.get('link'),
            'content_jp': news_source.get('content_jp'),
            'content_cn': news_source.get('content_cn'),
            'category': news_source.get('category'),
            'pub_date': news_source.get('pub_date'),
            'get_date': news_source.get('get_date')
        }
        return response(code=200, message="成功获取新闻详情", data=news_data)
    else:
        # 如果没有找到新闻，返回错误信息
        return response(code=400, message="未找到新闻", data=None)
