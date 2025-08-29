from aiogram.enums import ContentType

from resources import funcs


class MessageActivityData:
    def __init__(self,
                 user_id: int = 0,
                 content_type: ContentType = ContentType.TEXT,
                 date: str = None,
                 text_size: int = 0,
                 is_forward: bool = False):
        self.user_id = user_id
        self.content_type = content_type
        self.date = funcs.to_utc(date)
        self.text_size = text_size
        self.is_forward = is_forward
