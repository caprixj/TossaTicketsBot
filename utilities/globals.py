from utilities.run_mode import RunModeSettings

CONFIG_PATH_DEV = 'config/config.xml'
CONFIG_PATH_PROD = '../config/config.xml'

CREATOR_USER_ID = 825549745
CREATOR_USERNAME = '@capri_xj'

TPAY_YES_CALLBACK = 'tpay_yes'
TPAY_NO_CALLBACK = 'tpay_no'

ADDT_TEXT = '📈 тікети нараховано!'
DELT_TEXT = '📉 тікети знято!'
SETT_TEXT = '🔄 тікети перевстановлено!'
TPAY_TEXT = '🔀 тікети переведено!'
TOPT_DESC_TEXT = '*💸 рейтинг тікетів*'
TOPT_ASC_TEXT = '*💩 анти-рейтинг тікетів*'
INFM_TEXT = '<b>ℹ️ інформація про учасника</b>'
SQL_SUCCESS_TEXT = '✅ команду виконано!'
SQL_FAILED_TEXT = '❌ команду відхилено!'
GET_MEMBER_FAILED_TEXT = '❌ учасника не знайдено! перевірте правильність введеного ідентифікатора'
NO_NAMES_TEXT = '<unknown-dobvoyob>'
VALID_ARGS_TEXT = 'THE PROGRAM WAS STARTED WITH INVALID COMMAND ARGUMENTS!'
TOGGLE_CHAT_TEXT = '🪬 гіпер пупер секретний режим ГУР'
SERVICE_OPERATION_NONE_RESULT_TEXT = '😔 не вдалося виконати операцію..'
GENERATE_CALLBACK_DATA_ERROR_TEXT = 'cannot generate callback data with given callback args'
ALERT_CALLBACK_ACTIVE_TEXT = "не тикай! операція вже виконується..."
ALERT_CALLBACK_YES_TEXT = "ви не можете підтвердити цю операцію!"
ALERT_CALLBACK_NO_TEXT = "ви не можете скасувати цю операцію!"
NOT_IMPLEMENTED_TEXT = "ще не реалізовано :с"

HELP_TEXT = """
перелік доступних команд
\n/help - виводить перелік доступних команд
\n/toptall - виводить актуальний рейтинг спільноти за к-стю тікетів на балансі
\n/topt <number> - команда, аналогічна до toptall, проте необхідно вказувати потрібну к-сть місць в аргументах. додатнє число для звичайного рейтингу, від'ємне число для анти-рейтингу. наприклад, "/topt 5" виведе перші п'ять місць у списку, "/topt -3" виведе перші три з кінця
\n/bal - виводить поточний баланс тікетів. щоб дізнатися власний баланс, просто пропишіть команду. щоб дізнатися чужий баланс, пропишіть команду у відповідь на повідомлення учасника
\n/infm - виводить загальну інформацію про учасника спільноти. щоб дізнатися про себе, просто пропишіть команду. щоб дізнатися про іншого учасника, пропишіть команду у відповідь на його повідомлення
"""

# RunModeSettings | defined in main.py | stored in config.xml
# bot_token, group_chat_id, db_file_path
rms = RunModeSettings()
