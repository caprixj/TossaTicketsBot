from utilities.run_mode import RunModeSettings

# RunModeSettings | defined in main.py | stored in config.xml
# bot-token, group-chat-id, db-backup-chat-id, db-file-path
rms: RunModeSettings = RunModeSettings()

CONFIG_PATH_DEV = 'config/config.xml'
CONFIG_PATH_PROD = '../config/config.xml'

CREATOR_USER_ID = 825549745
CREATOR_USERNAME = '@capri_xj'

FEE_RATE = 0.27  # F
MIN_FEE = 1      # M

TICKETS_ARG = 'tickets'
DESCRIPTION_ARG = 'description'
USERNAME_ARG = 'username'
USER_ID_ARG = 'user_id'
QUERY_ARG = 'query'
MESSAGE_ARG = 'message'
SIZE_ARG = 'size'

TPAY_YES_CALLBACK = 'tpay_yes'
TPAY_NO_CALLBACK = 'tpay_no'
TPAY_FEE_INCORPORATION_CALLBACK = 'tpay_fi'

RESET_TPAY_AVAILABLE_DONE = 'ℹ️ к-сть доступних переказів оновлено'
DB_BACKUP_DONE = 'ℹ️ копію бази даних збережено'

ADDT_TEXT = '📈 тікети нараховано!'
DELT_TEXT = '📉 тікети знято!'
SETT_TEXT = '🔄 тікети перевстановлено!'
TPAY_TEXT = '🔀 тікети переведено!'
REG_SUCCESS = '🎉 реєстрація пройшла успішно!\nласкаво просимо в тікетономіку'
REG_DENIED_CTT_NONE = '❌ відхилено! ви вже берете участь у тікетономіці!'
REG_DENIED_CTT_REPLY = '❌ відхилено! даний учасник вже бере участь у тікетономіці!'
RUSNI_TEXT = 'пизда!'
TOPT_DESC = '*💸 рейтинг тікетів*'
TOPT_ASC = '*💩 анти-рейтинг тікетів*'
INFM_TEXT = '<b>ℹ️ інформація про учасника</b>'
SQL_SUCCESS = '✅ команду виконано!'
SQL_FAILED = '❌ команду відхилено!'
COM_PARSER_FAILED = '❌ відхилено! неправильно оформлена команда'
GET_MEMBER_FAILED = '❌ учасника не знайдено! перевірте правильність введеного ідентифікатора'
SERVICE_OPERATION_NONE_RESULT = '😔 не вдалося виконати операцію..'
ALERT_CALLBACK_YES = 'ви не можете підтвердити цю операцію!'
ALERT_CALLBACK_NO = 'ви не можете скасувати цю операцію!'
ALERT_CALLBACK_ACTION = 'ви не можете здійснити цю операцію!'
NOT_IMPLEMENTED = 'ще не реалізовано :с'
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

🪬 Аби взяти участь у тікетономіці, необхідно вступити в нашу Спільноту, у телеграм групу *Spaceflight Simulator 🇺🇦* (@spaceflight\_simulator\_chat), та відправити в групі будь-яку команду тікето-тяночці

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
