# scheduler.py
import threading
import time

from News.news_service.news_fetcher import fetch_and_store_news
from News.shared_lib.config.constant import Config


def run_fetcher(categories):
    """
    执行新闻抓取任务的函数。
    :param categories: 要抓取的新闻类别列表。
    """
    while True:
        start_time = time.time()  # 记录开始时间

        fetch_and_store_news(categories)

        end_time = time.time()  # 记录结束时间
        duration = (end_time - start_time) / 60  # 计算运行时长并转换为分钟

        print(f"本次执行时间: {duration:.2f} 分钟")
        print("等待下一次执行")
        time.sleep(Config.UPDATE_INTERVAL)


if __name__ == '__main__':
    # # 获取所有新闻类别，并分成两部分
    # categories = list(Config.TOPICS.keys())
    # half_point = len(categories) // 2
    #
    # # 将类别列表分成两部分
    # categories_1 = categories[:half_point]
    # categories_2 = categories[half_point:]
    #
    # # 创建两个线程，每个线程负责一部分新闻类别的抓取
    # fetcher_thread_1 = threading.Thread(target=run_fetcher, args=(categories_1,))
    # fetcher_thread_2 = threading.Thread(target=run_fetcher, args=(categories_2,))
    #
    # # 启动两个线程
    # fetcher_thread_1.start()
    # fetcher_thread_2.start()
    #
    # # 等待两个线程完成
    # fetcher_thread_1.join()
    # fetcher_thread_2.join()

    categories = list(Config.TOPICS.keys())
    quarter_point = len(categories) // 4

    # 将类别列表分成四部分
    categories_1 = categories[:quarter_point]
    categories_2 = categories[quarter_point:2 * quarter_point]
    categories_3 = categories[2 * quarter_point:3 * quarter_point]
    categories_4 = categories[3 * quarter_point:]

    # 创建四个线程
    fetcher_thread_1 = threading.Thread(target=run_fetcher, args=(categories_1,))
    fetcher_thread_2 = threading.Thread(target=run_fetcher, args=(categories_2,))
    fetcher_thread_3 = threading.Thread(target=run_fetcher, args=(categories_3,))
    fetcher_thread_4 = threading.Thread(target=run_fetcher, args=(categories_4,))

    # 启动线程
    fetcher_thread_1.start()
    fetcher_thread_2.start()
    fetcher_thread_3.start()
    fetcher_thread_4.start()

    # 等待线程完成
    fetcher_thread_1.join()
    fetcher_thread_2.join()
    fetcher_thread_3.join()
    fetcher_thread_4.join()
