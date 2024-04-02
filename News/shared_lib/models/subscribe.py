# subscript.py

class Subscription:
    def __init__(self, phone_number, category):
        self.phone_number = phone_number
        self.category = category

    def to_dict(self):
        return {
            "phone_number": self.phone_number,
            "category": self.category
        }
