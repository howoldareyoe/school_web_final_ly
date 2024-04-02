# translate_util.py

from googletrans import Translator
from pygtrans import Translate


# 翻译文本
def translate_text_origin(text, src_language, dest_language):
    """
    使用 Google 翻译库翻译文本。
    :param text: 要翻译的文本。
    :param src_language: 源语言代码。
    :param dest_language: 目标语言代码。
    :return: 翻译后的文本。
    """
    translator = Translator()
    try:
        translation = translator.translate(text, src=src_language, dest=dest_language)
        return translation.text
    except Exception as e:
        print(f"翻译过程中发生错误: {e}")
        return None


def translate_text(text, src_language, dest_language):
    client = Translate()
    response = client.translate(text, 'zh-CN')
    return response.translatedText
