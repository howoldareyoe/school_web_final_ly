from flask import Blueprint, request

from News.shared_lib.config.constant import Config
from News.shared_lib.utils.es_util import ElasticsearchClient
from News.shared_lib.utils.response_util import response

search_bp = Blueprint('search', __name__)


@search_bp.route('/', methods=['GET'])
def search_news():
    keyword = request.args.get('keyword', '')
    category = request.args.get('category', '')
    page = int(request.args.get('page', 1))

    if not keyword or not category:
        return response(code=400, message="缺少关键词和新闻类别")

    # 按空格分割关键词
    keywords = keyword.split()

    es_client = ElasticsearchClient()
    search_result = es_client.search_news_by_keywords(keywords=keywords, category=category,
                                                      page=page, per_page=Config.PER_PAGE)

    # 处理搜索结果
    if search_result["total"] == 0:
        return response(code=400, message="没有找到符合条件的新闻")

    news_list = [{
        'id': news['_id'],
        'title': news.get('title'),
        'link': news.get('link'),
        'category': news.get('category'),
        'pub_date': news.get('pub_date'),
        'get_date': news.get('get_date')
    } for news in search_result["news"]]

    return response(code=200, data={"total": search_result["total"], "news": news_list}, message="搜索成功")
