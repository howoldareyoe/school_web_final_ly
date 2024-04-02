# news.py

class News:
    def __init__(self, title, link, content_cn, content_jp, category, pub_date, get_date):
        self.title = title
        self.link = link
        self.content_cn = content_cn
        self.content_jp = content_jp
        self.category = category
        self.pub_date = pub_date
        self.get_date = get_date

    def to_dict(self):
        return {
            "title": self.title,
            "link": self.link,
            "content_cn": self.content_cn,
            "content_jp": self.content_jp,
            "category": self.category,
            "pub_date": self.pub_date,
            "get_date": self.get_date
        }
