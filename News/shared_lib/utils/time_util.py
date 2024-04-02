# time_util.py

from datetime import datetime, timedelta

import pytz  # 导入 pytz 库来处理时区


class TimeUtils:
    @staticmethod
    def get_formatted_time(time_str=None, format="%Y年%m月%d日 %H:%M"):
        """
        将时间字符串转换为指定格式。
        """
        if time_str:
            time_obj = datetime.strptime(time_str, "%a, %d %b %Y %H:%M:%S GMT")
        else:
            time_obj = datetime.now()
        return time_obj.strftime(format)

    @staticmethod
    def datetime_serializer(obj):
        """
        将datetime对象序列化为指定格式的字符串
        :param obj: 要序列化的datetime对象
        :return: 序列化后的字符串，格式为"年-月-日 时:分"
        """
        if isinstance(obj, datetime):
            return obj.strftime("%Y年%m月%d日 %H:%M")
        raise TypeError("Type not serializable")

    @staticmethod
    def convert_to_beijing_time(gmt_time_str):
        """
        将国际标准时间 (GMT/UTC) 的日期时间字符串转换为北京时间字符串
        :param gmt_time_str:  包含日期时间的国际标准时间 (GMT/UTC) 字符串
        :return: 包含日期时间的北京时间字符串，格式为"年-月-日 时:分"
        """
        # 创建一个时区对象，用于表示中国北京时区
        beijing_tz = pytz.timezone('Asia/Shanghai')

        # 将日期时间字符串解析为 datetime 对象（原始字符串的格式为 RFC1123）
        gmt_time = datetime.strptime(gmt_time_str, "%a, %d %b %Y %H:%M:%S GMT")

        # 使用 astimezone 将时区从 UTC 转换为北京时区
        beijing_datetime = gmt_time.replace(tzinfo=pytz.utc).astimezone(beijing_tz)

        # 使用 strftime 格式化日期时间对象为指定格式
        beijing_time_str = beijing_datetime.strftime('%Y年%m月%d日 %H:%M')

        return beijing_time_str

    @staticmethod
    def parse_rfc1123_to_iso8601(rfc1123_str):
        """
        将 RFC 1123 格式的时间字符串转换为 ISO 8601 格式
        """
        gmt_time = datetime.strptime(rfc1123_str, "%a, %d %b %Y %H:%M:%S GMT")
        return gmt_time.isoformat()

    @staticmethod
    def get_current_time_iso8601():
        """
        获取当前时间的 ISO 8601 格式字符串
        """
        return datetime.now().isoformat()

    @staticmethod
    def get_past_hour_to_previous_day_time_range(now=None):
        """
        计算从前半个小时到前一天同一时间点的时间范围。
        :param now: 可选的当前时间 datetime 对象。如果未提供，则使用当前系统时间。
        :return: 一个元组，包含格式化的开始和结束时间字符串。
        """
        if not now:
            now = datetime.now()

        # 计算前一天的相同时间
        start_time = (now - timedelta(days=1)).replace(minute=0, second=0, microsecond=0)

        # 计算当前时间的前半小时
        end_time = now - timedelta(minutes=30)

        # 格式化时间
        formatted_start_time = start_time.strftime("%Y年%m月%d日 %H:%M")
        formatted_end_time = end_time.strftime("%Y年%m月%d日 %H:%M")

        return formatted_start_time, formatted_end_time
