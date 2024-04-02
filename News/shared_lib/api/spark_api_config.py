import logging

from . import spark_api

# 以下密钥信息从控制台获取
appid = "xxxxx"  # 填写控制台中获取的 APPID 信息
api_secret = "xxx"  # 填写控制台中获取的 APISecret 信息
api_key = "xxx"  # 填写控制台中获取的 APIKey 信息

# 用于配置大模型版本，默认“general/generalv2”
domain = "generalv2"  # v2.0版本

# 云端环境的服务地址
Spark_url = "ws://spark-openapi.cn-huabei-1.xf-yun.com/v1/assistants/gbxpcy4u3t48_v1"  # v2.0环境的地址

text = []


def getText(role, content):
    jsoncon = {}
    jsoncon["role"] = role
    jsoncon["content"] = content
    text.append(jsoncon)
    return text


def getlength(text):
    length = 0
    for content in text:
        temp = content["content"]
        leng = len(temp)
        length += leng
    return length


def checklen(text):
    while (getlength(text) > 8000):
        del text[0]
    return text


def summary_with_ai(Input):
    text.clear()
    question = checklen(getText("user", Input))
    spark_api.answer = ""
    spark_api.main(appid, api_key, api_secret, Spark_url, domain, question)
    getText("assistant", spark_api.answer)
    # logging.debug("%r", text)
    return text[1]['content']
