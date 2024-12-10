import random

from utilities.constant import CREATOR_USERNAME


async def get_random_permission_denied_message() -> str:
    messages = [
        f"пизда тобі. {CREATOR_USERNAME} ходь сюди",
        f"дохуя розумний? я кличу {CREATOR_USERNAME}",
        f"безкоштовних тікетів не буває. ставай раком, {CREATOR_USERNAME} скоро підійде",
        "з'єбався з чату. шоб я тебе більше тут не бачила",
        "адмінка ще не виросла, клуша",
        "хто тобі дав право змінювати свій баланс тікетів, дура?",
        "вам нараховано 1488 тікетів (іди нахуй)",
        "в рот тебе єбала",
        "тобі б навіть шлюха підзаборна не дала",
        "я подзвоню твоїй мамі і скажу, шо ти поганий хлопчик",
        "це м'яско забагато собі дозволяє..",
        "в бан його нахуй. я вже заєбалася..",
        "коли цього вже цього лошпеда забанять?",
        "лівай чат, уебище",
        "даю тобі можливість покинути чат самостійно..",
        f"цікаво, шо тепер з тобою зробить {CREATOR_USERNAME}.. співчуваю",
        "лох",
        "лошара",
        "не хочу",
        "не буду",
        "іди нахуй. не можна",
        "іди нахуй",
        "пішов ти нахуй",
        "іди в пизду",
        "гуляй лісом",
        "гуляй нахуй",
        "гуляй, хлопче",
        "бан хочеш?",
        "пососи",
        "а нахуй не хочеш сходити?",
        "чітер єбучий"
    ]

    return messages[random.randint(0, len(messages) - 1)]


async def get_command_args(message_text: str) -> list[str]:
    if not message_text:
        return list()

    split = message_text.split(" ")
    split_stripped = []

    for i in split:
        if i != "":
            split_stripped.append(i)

    split_stripped.remove(split_stripped[0])

    return split_stripped
