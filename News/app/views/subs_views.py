from flask import Blueprint, request
from News.shared_lib.models.subscribe import Subscription
from News.shared_lib.utils.es_util import ElasticsearchClient
from News.shared_lib.utils.response_util import response
from News.subscriber_service.sender import sender_for_one
import threading


subs_bp = Blueprint('subs', __name__)


# 测试
@subs_bp.route('/', methods=['GET'])
def test():
    client = ElasticsearchClient()
    subs_item = Subscription(phone_number='15336513769', category='IT')
    client.index_subs_item(subs_item.to_dict())
    # client.delete_subs_item(phone_number='15336513769', news_category='国际', index_name='subscribers')
    recent_documents = client.get_latest_ten('国际')

    # 创建一个空列表来存储内容
    contents_translated = []
    for doc in recent_documents:
        # 获取文档的内容
        content = doc["content_cn"]

        contents_translated.append(content)
        # 打印内容
        # print(f"Content: {content}")

    # 将列表转换为字符串，每个内容之间空两行
    contents_str = "\n\n".join(contents_translated)

    # 打印字符串
    print(contents_str)


@subs_bp.route('/subscribe', methods=['POST'])
def subscribe():
    data = request.json  # 获取JSON格式的请求体数据
    category = data.get('category', None)
    phone_number = data.get('number', None)

    client = ElasticsearchClient()
    # 使用search_for_subscriber方法查询是否已经存在具有相同phone_number和category的订阅者
    response_from_es = client.search_for_subscriber(phone_number, category)

    # 如果已经存在，则返回错误信息
    if response_from_es.hits.total.value > 0:
        return response(code=400, message="该手机号已经订阅过此类别", data=None)

    # 否则，插入新的订阅者信息
    subs_item = Subscription(phone_number=phone_number, category=category)
    client.index_subs_item(subs_item.to_dict())

    # 创建一个新的线程来执行sender_for_one函数
    thread = threading.Thread(target=sender_for_one, args=(phone_number, category))
    thread.start()

    return response(code=200, message="订阅成功", data=None)


@subs_bp.route('subscribe/cancel', methods=['POST'])
def unsubscribe():
    data = request.json  # 获取JSON格式的请求体数据
    category = data.get('category', None)
    phone_number = data.get('number', None)
    client = ElasticsearchClient()
    client.delete_subs_item(phone_number=phone_number, news_category=category)

    return response(code=200, message="取消订阅成功", data=None)
