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
    MEMBER_INFO_TEXT = '<b>ℹ️ інформація про учасника</b>'
    MEMBER_TICKETS_COUNT_TEXT = '💳 тікетів'
    SQL_EXECUTE_SUCCEED_TEXT = '✅ команду виконано!'
    SQL_EXECUTE_FAILED_TEXT = '❌ команду відхилено!'
    NO_NAMES_TEXT = '<unknown-dobvoyob>'
    VALID_ARGS_TEXT = 'THE PROGRAM WAS STARTED WITH INVALID COMMAND PARAMETERS!'

    HELP_TEXT = """
🇺🇦 перелік доступних команд
\n/help - виводить перелік доступних команд
\n/toptall - виводить актуальний рейтинг спільноти за к-стю тікетів на балансі
\n/topt <number> - команда, аналогічна до toptall, проте необхідно вказувати потрібну к-сть місць в аргументах. додатнє число для звичайного рейтингу, від'ємне число для анти-рейтингу. наприклад, "/topt 5" виведе перші п'ять місць у списку, "/topt -3" виведе перші три з кінця
\n/bal - виводить поточний баланс тікетів. щоб дізнатися власний баланс, просто пропишіть команду. щоб дізнатися чужий баланс, пропишіть команду у відповідь на повідомлення учасника
\n/infm - виводить загальну інформацію про учасника спільноти. щоб дізнатися про себе, просто пропишіть команду. щоб дізнатися про іншого учасника, пропишіть команду у відповідь на його повідомлення
\n\n🇬🇧 list of available commands
\n/help - displays a list of available commands
\n/toptall - displays the current community ranking by the number of tickets on the balance
\n/topt <number> - a command similar to toptall, but you must specify the desired number of places in the arguments. a positive number for a regular rating, a negative number for an anti-rating. For example, "/topt 5" will display the first five places in the list, "/topt -3" will display the first three from the end
\n/bal - displays the current ticket balance. To find out your own balance, simply type the command. To find out someone else's balance, type the command in reply to a infm's message
\n/infm - displays general information about a community infm. To find out about yourself, simply type the command. To find out about another infm, write the command in response to his message
"""

    # RunModeSettings | defined in main.py | stored in config.xml
    # bot_token, group_chat_id, db_file_path
    rms = RunModeSettings()
