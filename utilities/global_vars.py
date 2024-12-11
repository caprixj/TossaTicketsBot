from model.functional.RunModeSettings import RunModeSettings


class GlobalVariables:
    CONFIG_PATH_DEV = 'config/config.xml'
    CONFIG_PATH_PROD = '../config/config.xml'

    CREATOR_USER_ID = 825549745
    CREATOR_USERNAME = '@capri_xj'

    WRONG_COMMAND_ARGUMENTS_TEXT = "відхилено. помилкові аргументи"
    TICKETS_ADDED_TEXT = "тікети нараховано ^-^"
    NO_REPLY_TEXT = "команда має бути у відповідь на повідомлення людини або мати юзернейм в аргументах"
    MEMBER_TICKETS_COUNT_TEXT = "поточний баланс"
    NO_NAMES_TEXT = "не шановна особа"

    # RunModeSettings | defined in main.py | stored in config.xml
    # bot_token, group_chat_id, db_file_path
    rms = RunModeSettings()
