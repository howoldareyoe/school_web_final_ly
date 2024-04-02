import datetime
import time
import threading
from News.shared_lib.api.spark_api_config import summary_with_ai
from News.shared_lib.api.tencent_sms_api import send_template_sms
from News.shared_lib.config.constant import Config
from News.shared_lib.utils.es_util import ElasticsearchClient

contents_dict = {}


def get_latest_ten_news_summed():
    es_client = ElasticsearchClient()

    for topic in Config.TOPICS.keys():
        recent_documents = es_client.get_latest_ten(topic)

        # 创建一个空列表来存储内容
        contents_translated = [topic]
        for doc in recent_documents:
            # 获取文档的内容
            content = doc["content_cn"]
            # 获取摘要并将其长度限制为10个字符
            # summary = summary_with_ai(content)
            # TODO 待summa
            summary = content
            if summary:
                if len(summary) > 12:
                    summary = summary[:9] + "..."
                contents_translated.append(summary)
            else:
                contents_translated.append("由于涉及敏感信息不推送")

        contents_dict[topic] = contents_translated
    return contents_dict


def sender_for_everyone():
    get_latest_ten_news_summed()
    es_client = ElasticsearchClient()
    res = es_client.get_subs_grouped_data()
    for phone_number, categories in res.items():
        for category in categories:
            # send_template_sms("+86" + phone_number, contents_dict[category])
            # TODO 向每一位发送
            print(phone_number, category)

            # print(res)


def sender_for_one(phone_number, topic):
    es_client = ElasticsearchClient()
    recent_documents = es_client.get_latest_ten(topic)
    # 创建一个空列表来存储内容
    contents_translated = [topic]
    for doc in recent_documents:
        # 获取文档的内容
        content = doc["content_cn"]
        print("content:", content)
        # 获取摘要并将其长度限制为10个字符
        summary = summary_with_ai(content)
        if summary:
            if len(summary) > 12:
                summary = summary[:9] + "..."
            contents_translated.append(summary)
        else:
            contents_translated.append("由于涉及敏感信息不推送")
    res = send_template_sms("+86" + phone_number, contents_translated)
    print(contents_translated)
    print(res)


def run_sender_every_hour():
    while True:
        now = datetime.datetime.now()
        next_hour = datetime.datetime(now.year, now.month, now.day, now.hour) + datetime.timedelta(hours=1)
        sleep_time = (next_hour - now).seconds
        sender_for_everyone()
        time.sleep(sleep_time)  # 暂停到下一个整点小时


if __name__ == '__main__':
    thread = threading.Thread(target=run_sender_every_hour)
    thread.start()
    # sender_for_one('15336513769', '国际')
