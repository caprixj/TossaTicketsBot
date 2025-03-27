from model.types.run_mode import RunModeSettings

# RunModeSettings | defined in main.py | stored in config.xml
# bot-token, group-chat-id, db-backup-chat-id, db-file-path
rms: RunModeSettings = RunModeSettings()

CONFIG_PATH_DEV = 'config/config.xml'
CONFIG_PATH_PROD = '../../config/config.xml'

CREATOR_USER_ID = 825549745
CREATOR_USERNAME = '@capri_xj'

FEE_RATE = 0.27  # F
MIN_FEE = 1      # M

PAGE_ROW_CHAR_LIMIT = 25
PAGE_ROWS_COUNT_LIMIT = 40

TICKETS_ARG = 'tickets'
DESCRIPTION_ARG = 'description'
USERNAME_ARG = 'username'
USER_ID_ARG = 'operation_id'
QUERY_ARG = 'query'
MESSAGE_ARG = 'page_message'
SIZE_ARG = 'size'
AWARD_ID_ARG = 'award_id'
PAGE_ARG = 'page'

TPAY_YES_CALLBACK = 'tpay_yes'
TPAY_NO_CALLBACK = 'tpay_no'
TPAY_FEE_INCORPORATION_CALLBACK = 'tpay_fi'
HELP_DEL_CALLBACK = 'help_del'
MYTPAY_BACK_CALLBACK = 'mytpay_back'
MYTPAY_FORWARD_CALLBACK = 'mytpay_forward'
MYTPAY_HIDE_CALLBACK = 'mytpay_hide'
DECORATIVE_KEYBOARD_BUTTON = 'decorative'

RESET_TPAY_AVAILABLE_DONE = 'ℹ️ к-сть доступних переказів оновлено'
DB_BACKUP_DONE = 'ℹ️ копію бази даних збережено'

MYTPAY_TITLE = '📊 Історія надходжень та витрат (тікети)'
MYTPAY_START_TEXT = """
🔹 - вхідні перекази
🔻 - вихідні перекази
🔀 - переказ за tpay
✨ - переказ за addt/delt/sett
"""

ADDT_TEXT = '📈 тікети нараховано!'
DELT_TEXT = '📉 тікети знято!'
SETT_TEXT = '🔄 тікети перевстановлено!'
TPAY_TEXT = '🔀 тікети переведено!'
AWARD_SUCCESS = '🎖 шановного учасника нагороджено!'
REG_SUCCESS = '🎉 реєстрація пройшла успішно!\nласкаво просимо в тікетономіку'
RUSNI_TEXT = 'пизда!'
TOPT_DESC = '*💸 рейтинг тікетів*'
TOPT_ASC = '*💩 анти-рейтинг тікетів*'
INFM_TEXT = '<b>ℹ️ інформація про учасника</b>'
SQL_SUCCESS = '✅ команду виконано!'
NOT_IMPLEMENTED = 'ще не реалізовано :с'

ALERT_CALLBACK_YES = 'ви не можете підтвердити цю операцію!'
ALERT_CALLBACK_NO = 'ви не можете скасувати цю операцію!'
ALERT_CALLBACK_ACTION = 'ви не можете здійснити цю операцію!'
CALLBACK_FLOOD_CONTROL = 'не так швидко! такими темпами телеграм пошле тікето-тяночку нахуй.. (зачекай щонайменше 20 секунд)'

AWARD_DUPLICATE = '❌ учасник уже має вказану нагороду!'
REG_DENIED_CTT_NONE = '❌ ви вже берете участь у тікетономіці!'
REG_DENIED_CTT_REPLY = '❌ даний учасник вже бере участь у тікетономіці!'
SQL_FAILED = '❌ команду відхилено!'
COM_PARSER_FAILED = '❌ неправильно оформлена команда!'
TARGET_NOT_MEMBER_ERROR = '❌ вказаний користувач не є учасником тікетономіки!'
GET_MEMBER_FAILED = '❌ учасника не знайдено! перевірте правильність введеного ідентифікатора'
GET_AWARD_FAILED = '❌ вказаної нагороди не існує! перевірте правильність введеного ідентифікатора'
SERVICE_OPERATION_NONE_RESULT = '😔 не вдалося виконати операцію..'
NOT_MEMBER_ERROR = '❌ щоб користуватися ботом, необхідно бути учасником чату сфс та відправити команду /reg. детальніші інструкції шукай на /help'

INVALID_ARGS = 'THE PROGRAM WAS STARTED WITH INVALID COMMAND ARGUMENTS!'
NO_OVERLOADS_ERROR = 'PARSING WITHOUT OVERLOADS IN COMMAND PARSER!'
DOUBLE_TARGETING_ERROR = 'TRYING TO PUT TWO TARGET-TYPED ARGUMENTS INTO COMMAND OVERLOAD!'
CREATOR_REQUIRED_VIOLATION = 'CREATOR_REQUIRED_VIOLATION'

HELP_TEXT = """
✨ *Тікето-тяночка 🇺🇦* ✨

*Тікето-тяночка* — це телеграм бот для автоматизації процесів *Тікетономіки*. 
_Май на увазі, що бот хоститься на телефоні розробника, тож не завжди може бути доступним_

*Тікетономіка* — це ігрова система, побудована на *тікетах* (ігровій валюті). Додаткова інформація та новини в телеграм каналі *TossaTickets* (https://t.me/+q66chy227wk5MWQy)

🪬 Аби взяти участь у тікетономіці, необхідно вступити в нашу Спільноту, у телеграм групу *Spaceflight Simulator 🇺🇦* (@spaceflight\_simulator\_chat), та відправити команду /reg тікето-тяночці

*📊 Дізнавайся про учасників та рейтинги*

*• Інформація про учасника*: Відправ у відповідь на повідомлення учасника _(= зроби реплай)_`  /infm `, або вкажи його username чи id` /infm [username/id]`
*• Переглянути активи учасника*: Зроби реплай` /bal`, або вкажи username чи id учасника` /bal [username/id]`
*• Рейтинг учасників за кількістю тікетів*: Отримай повний список` /topt`. Отримай обрізаний список, _(вказуючи додатнє число)_ або відповідний анти-рейтинг _(вказуючи від'ємне число)_` /topt [число]`

*💳 Здійснюй переказ активів*

*• Переказ тікетів між учасниками*: Зроби реплай на будь-яке повідомлення отримувача коштів, за бажання додай опис _(він збережеться)_` /tpay [число] [опис]`, або вкажи його username чи id` /tpay [username/id] [число] [опис]`. Допускаються додатні дробні та цілі числа _(максимум з двома цифрами після коми/крапки)_

*✉️ Маєш питання?*

• Підтримка: @capri\_xj
• GitHub: github.com/caprixj/TossaTicketsBot
"""
