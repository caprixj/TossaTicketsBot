from model.types.run_mode import RunModeSettings

# RunModeSettings | defined in main.py | stored in config.xml
# bot-token, group-chat-id, db-backup-chat-id, db-file-path
rms: RunModeSettings = RunModeSettings()

CONFIG_PATH_DEV = 'config/config.xml'
CONFIG_PATH_PROD = '../config/config.xml'

CREATOR_USER_ID = 825549745
CREATOR_USERNAME = '@capri_xj'

DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'

FEE_RATE = 0.27  # F
MIN_FEE = 1      # M

INFLATION_ALPHA = 0.9
FLUCTUATION_GAUSS_SIGMA = 0.009
MAX_FLUCTUATION = 1.1
MIN_FLUCTUATION = 0.9
INITIAL_TPOOL = 2326.1

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
PERCENT_ARG = 'percent'
PRICE_ARG = 'price'

TPAY_YES_CALLBACK = 'tpay_yes'
TPAY_NO_CALLBACK = 'tpay_no'
TPAY_FEE_INCORPORATION_CALLBACK = 'tpay_fi'

DECORATIVE_KEYBOARD_BUTTON = 'decorative'

HELP_HIDE_CALLBACK = 'help_hide'
AWARD_HIDE_CALLBACK = 'award_hide'
TOPT_HIDE_CALLBACK = 'topt_hide'

PV_BACK_CALLBACK = 'pv_back'
PV_FORWARD_CALLBACK = 'pv_forward'
PV_HIDE_CALLBACK = 'pv_hide'

LAWARD_TITLE = '<b>📯 Дошка нагород</b>'
LTRANS_TITLE = '📊 Історія надходжень та витрат (тікети)'
LTRANS_START_TEXT = """
🔹 - вхідні перекази
🔻 - вихідні перекази
🔀 - переказ за tpay
✨ - переказ за addt/delt/sett
"""

RESET_TPAY_AVAILABLE_DONE = 'ℹ️ к-сть доступних переказів оновлено'
DB_BACKUP_DONE = 'ℹ️ копію бази даних збережено'
PRICE_RESET_DONE = 'ℹ️ інфляційний курс тікетів оновлено'
SALARIES_PAID_OUT = 'ℹ️ нараховано заробітні плати'

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
*• Переглянути нагороди учасника*: Команда` /laward`. Працює аналогічно до` /bal`
*• Переглянути історію власних переказів*: Команда` /ltrans`
*• Рейтинг учасників за кількістю тікетів*: Отримай повний список` /topt`. Отримай обрізаний список, _(вказуючи додатнє число)_ або відповідний анти-рейтинг _(вказуючи від'ємне число)_` /topt [число]`
*• Рейтинг учасників за часткою тікетів*: Отримай рейтинг, аналогічний до` /topt` , але у відсотках:` /topt % [число]`

*💳 Здійснюй переказ активів*

*• Переказ тікетів між учасниками*: Зроби реплай на будь-яке повідомлення отримувача коштів, за бажання додай опис _(він збережеться)_` /tpay [число] [опис]`, або вкажи його username чи id` /tpay [username/id] [число] [опис]`. Допускаються додатні дробні та цілі числа _(максимум з двома цифрами після коми/крапки)_

*✉️ Маєш питання?*

• Автор: t.me/capri\_xj
• GitHub: github.com/caprixj/TossaTicketsBot
"""
