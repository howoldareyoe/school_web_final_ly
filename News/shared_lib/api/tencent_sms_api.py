import json

from tencentcloud.common import credential
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.sms.v20210111 import sms_client, models

sms_sdk_app_id = "1400876893"
template_id = "2026502"
secret_id = "AKID0vwv21pRr9LQQURFEINGC675xnZBZkhQ"
secret_key = "e6LNMG1hnjbCdsy0vmXAeyLgt4KTRE1s"


def send_template_sms(phone_number, template_params):
    try:
        # 实例化一个认证对象
        cred = credential.Credential(secret_id, secret_key)

        # 实例化一个http选项
        httpProfile = HttpProfile()
        httpProfile.endpoint = "sms.tencentcloudapi.com"

        # 实例化一个client选项
        clientProfile = ClientProfile()
        clientProfile.httpProfile = httpProfile

        # 实例化要请求产品的client对象
        client = sms_client.SmsClient(cred, "ap-nanjing", clientProfile)

        # 实例化一个请求对象
        req = models.SendSmsRequest()
        params = {
            "PhoneNumberSet": [phone_number],
            "SmsSdkAppId": sms_sdk_app_id,
            "SignName": "分享岛公众号",
            "TemplateId": template_id,
            "TemplateParamSet": template_params  # 使用模板的参数字典
        }
        req.from_json_string(json.dumps(params))

        # 返回的resp是一个SendSmsResponse的实例
        resp = client.SendSms(req)

        # 输出json格式的字符串回包
        return resp.to_json_string()

    except TencentCloudSDKException as err:
        return str(err)


if __name__ == "__main__":
    phone_number = "+8615336513769"
    template_params = [
        "栏目名称",
        "第一条新闻内容",
        "第二条新闻内容",
        "第三条新闻内容",
        "第四条新闻内容",
        "第五条新闻内容",
        "第六条新闻内容",
        "第七条新闻内容",
        "第八条新闻内容",
        "第九条新闻内容",
        "第十条新闻内容"
    ]

    result = send_template_sms(phone_number, template_params)
    print(result)
