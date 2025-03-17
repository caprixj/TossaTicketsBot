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
✨ *Тікето-тяночка 🇺🇦* ✨

*Тікето-тяночка* — це телеграм бот для автоматизації деяких процесів *Тікетономіки*. 
_Май на увазі, що бот хоститься на телефоні розробника, тож не завжди може бути доступним_

*Тікетономіка* — це ігрова система, побудована на *тікетах* (ігровій валюті) та телеграм каналі *TossaTickets* (https://t.me/+q66chy227wk5MWQy).

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

# RunModeSettings | defined in main.py | stored in config.xml
# bot_token, group_chat_id, db_file_path
rms = RunModeSettings()
