# date_util.py

import os
from datetime import datetime


class DateUtil:
    @staticmethod
    def is_date_range_valid(start_date, end_date):
        """
        检查日期范围是否有效
        :param start_date: 开始日期
        :param end_date: 结束日期
        :return: 布尔值，表示日期范围是否有效
        """
        start_path = os.path.join('data', start_date)
        end_path = os.path.join('data', end_date)
        return os.path.exists(start_path) and os.path.exists(end_path)

    @staticmethod
    def parse_date_param(date_str):
        """
        解析日期参数
        :param date_str: 日期字符串
        :return: datetime 对象或者在解析失败时返回 None
        """
        try:
            return datetime.strptime(date_str, '%Y-%m-%d-%H')
        except ValueError:
            return None
