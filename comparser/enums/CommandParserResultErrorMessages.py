from enum import Enum


class CommandParserResultErrorMessages(str, Enum):
    wrong_args = '❌ відхилено! помилкові аргументи'
    no_reply = '❌ відхилено! команда має бути у відповідь на повідомлення учасника групи'
    is_bot = '❌ відхилено! команда не може бути застосована до бота'
    no_overload_match = '❌ відхилено! команда не відповідає жодному з форматів'
    not_creator = '❌ відхилено!'
