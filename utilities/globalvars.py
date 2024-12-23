from utilities.runmode import RunModeSettings


class GlobalVariables:
    CONFIG_PATH_DEV = 'config/config.xml'
    CONFIG_PATH_PROD = '../config/config.xml'

    CREATOR_USER_ID = 825549745
    CREATOR_USERNAME = '@capri_xj'

    TICKETS_ADDED_TEXT = '📈 тікети нараховано!'
    TICKETS_REMOVED_TEXT = '📉 тікети знято!'
    TICKETS_SET_TEXT = '🔄 тікети перевстановлено!'
    TOPT_DESC_TEXT = '*💸 рейтинг тікетів*'
    TOPT_ASC_TEXT = '*💩 анти-рейтинг тікетів*'
    MEMBER_INFO_TEXT = 'ℹ️ повна інформація про учасника'
    MEMBER_TICKETS_COUNT_TEXT = '💳 поточний баланс'
    SQL_EXECUTE_SUCCEED_TEXT = '✅ команду виконано!'
    SQL_EXECUTE_FAILED_TEXT = '❌ команду відхилено!'
    NO_NAMES_TEXT = '<unknown-dobvoyob>'
    VALID_ARGS_TEXT = 'THE PROGRAM WAS STARTED WITH INVALID COMMAND PARAMETERS!'

    # RunModeSettings | defined in main.py | stored in config.xml
    # bot_token, group_chat_id, db_file_path
    rms = RunModeSettings()
