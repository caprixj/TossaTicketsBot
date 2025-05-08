from model.types.run_mode import RunModeSettings

# RunModeSettings | defined in main.py | stored in config.xml
# bot-token, group-chat-id, db-backup-chat-id, db-file-path
rms: RunModeSettings = RunModeSettings()

CONFIG_PATH_DEV = 'config/config.xml'
CONFIG_PATH_PROD = '../config/config.xml'

CREATOR_USER_ID = 825549745
CREATOR_USERNAME = '@capri_xj'

DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'

UNI_TAX = 0.17  # F
MIN_FEE = 1      # M

INFL_ALPHA = 0.9
FLUCT_GAUSS_SIGMA = 0.009
MAX_FLUCT = 1.1
MIN_FLUCT = 0.9
INIT_TPOOL = 1315.15  # 2025-03-17
# INIT_TPOOL = 4333.62  # 2025-05-06 00:25:00

PAGE_ROW_CHAR_LIMIT = 25
PAGE_ROWS_COUNT_LIMIT = 40

GEM_BASE_PRICE = 0.2972122
MIN_DELTA_GEM_RATE = 0.5
MAX_DELTA_GEM_RATE = 2.0
MAT_RANK_DEVAL = 0.8

GEM_FREQ_SIGMA = 0.4
MIN_GEM_COUNT_TBOX = 1
MAX_GEM_COUNT_TBOX = 47

MATERIALS_YAML_PATH = 'model/yaml/materials.yaml'
GEM_FREQ_YAML_PATH = 'model/yaml/gem_freq.yaml'
RECIPES_YAML_PATH = 'model/yaml/recipes.yaml'

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
ID_ARG = 'id'
PRICE_ARG = 'price'
EMPLOYEE_ARG = 'employee_position'

TPAY_YES_CALLBACK = 'tpay_yes'
TPAY_NO_CALLBACK = 'tpay_no'
TPAY_FEE_INCORPORATION_CALLBACK = 'tpay_fi'
TBOX_CALLBACK = 'tbox'

DECORATIVE_KEYBOARD_BUTTON = 'decorative'

HELP_HIDE_CALLBACK = 'help_hide'
AWARD_HIDE_CALLBACK = 'award_hide'
TOPT_HIDE_CALLBACK = 'topt_hide'
CLAIM_BHF_CALLBACK = 'claim_bhf'

PV_BACK_CALLBACK = 'pv_back'
PV_FORWARD_CALLBACK = 'pv_forward'
PV_HIDE_CALLBACK = 'pv_hide'

INVALID_ARGS = 'THE PROGRAM WAS STARTED WITH INVALID COMMAND ARGUMENTS!'
NO_OVERLOADS_ERROR = 'PARSING WITHOUT OVERLOADS IN COMMAND PARSER!'
DOUBLE_TARGETING_ERROR = 'TRYING TO PUT TWO TARGET-TYPED ARGUMENTS INTO COMMAND OVERLOAD!'
CREATOR_REQUIRED_VIOLATION = 'CREATOR_REQUIRED_VIOLATION'

RESET_TPAY_AVAILABLE_DONE = 'ℹ️ number of available transfers updated'
RESET_TBOX_AVAILABLE_DONE = 'ℹ️ number of available tboxes updated'
DB_BACKUP_DONE = 'ℹ️ database backup saved'
PRICE_RESET_DONE = 'ℹ️ the prices, artifact values and ticket inflation rate have been updated'
SALARIES_PAID_OUT = 'ℹ️ salaries paid'

CONTINUE_BTN = '✅ continue'
CANCEL_BTN = '❌ cancel'
INCORPORATE_FEE_BTN = '➕ tax inside'
HIDE_BTN = '🗑 hide'
OPEN_TBOX_BTN = '➡️ open!'
# CLAIM_BTN = '➡️ claim'

ADDT_TEXT = '📈 tickets added!'
DELT_TEXT = '📉 tickets removed!'
SETT_TEXT = '🔄 tickets reset!'
TPAY_TEXT = '🔀 tickets transferred!'
AWARD_SUCCESS = '🎖 the member has been awarded!'
REG_SUCCESS = '🎉 successfully signed up!\nwelcome to ticketonomics'
UNREG_TEXT = '☠️ mercilessly kicked out of ticketonomics'
RUSNI_TEXT = 'пизда!'
TOPT_DESC = '*💸 ticket leaderboard*'
TOPT_ASC = '*💩 ticket anti-leaderboard*'
INFM_TEXT = '<b>ℹ️ member information</b>'
TBOX_TEXT = '🎁 daily tbox'
TBOX_OPENED_TEXT = 'your tbox reward'
SQL_SUCCESS = '✅ command executed!'
MEMBER_HIRED = '✅💼 member hired for the position!'
RESET_PRICE_COMMAND_DONE = '✅ manual price reset executed based on the ticket inflation rate'
# SPAWN_BHF_TEXT = '🔨 banhammer fragments found!'
# BHF_CLAIMED_TEXT = '🔨 banhammer fragments claimed!\nby member'
MEMBER_ALREADY_HIRED = '❌ member already holds this position!'
MEMBER_FIRED = '❌💼 member has been fired!'
MEMBER_ALREADY_FIRED = '❌ cannot fire member as he does not hold this position!'
UNREG_CREATOR_ERROR = "i won't kill you, my lord! ♥️"
NOT_IMPLEMENTED = 'not implemented yet :('

ALERT_CALLBACK_YES = 'you cannot confirm this action!'
ALERT_CALLBACK_NO = 'you cannot cancel this action!'
ALERT_CALLBACK_ACTION = 'you cannot perform this action!'
CALLBACK_FLOOD_CONTROL = 'not so fast! at this rate, telegram will send ticketo-chan to hell.. (wait at least 20 seconds)'

AWARD_DUPLICATE = '❌ participant already has this award!'
REG_DENIED_CTT_NONE = '❌ you are already a participant in ticketonomics!'
REG_DENIED_CTT_REPLY = '❌ this participant is already part of ticketonomics!'
SQL_FAILED = '❌ command rejected!'
COM_PARSER_FAILED = '❌ invalid command format!'
TARGET_NOT_MEMBER_ERROR = '❌ the specified user is not a ticketonomics member!'
GET_MEMBER_FAILED = '❌ member not found! check the id you entered'
GET_AWARD_FAILED = '❌ specified award does not exist! check the id you entered'
SERVICE_OPERATION_NONE_RESULT = '😔 couldn’t complete the operation..'
NOT_MEMBER_ERROR = '❌ to use the bot, you must be a member of the sfs chat and send the /reg command. more instructions can be found at /help'
TBOX_UNAVAILABLE_ERROR = '❌ you already opened a tbox today!'

BAL_NAME = "🪪 name"
BAL_PERSONAL = '💳 personal account'
BAL_BUSINESS = '💸 business account'
BAL_TPAY_AVAILABLE = '🔀 tpay available'
BAL_TBOX_AVAILABLE = '🎁 tbox available'

BALM_BALANCE_EMPTY = 'you have no materials yet.. 😶‍🌫️'
BALM_NO_GEMSTONES = 'you have no gemstones yet.. 😶‍🌫️'
BALM_NO_INTERMEDIATES = 'you have no intermediates yet.. 😶‍🌫️'
BALM_NO_ARTIFACT_TEMPLATES = 'you have no artifact templates yet.. 😶‍🌫️'
BALM_TITLE = '<b>📦 materials account</b>'
BALM_START_TEXT = """
page 1 - gemstones
page 2 - intermediates
page 3 - artifact templates
"""

TBOX_MEMBER = '🪪 member'

LTRANS_TITLE = '<b>📊 income and expenses history (tickets)</b>'
LTRANS_START_TEXT = """
🔹 - incoming transfers  
🔻 - outgoing transfers  
🔀 - transfer via /tpay  
✨ - transfer by creator
"""
LTRANS_TRANS_HISTORY_EMPTY = 'your transactions history is empty.. 😶‍🌫️'
LTRANS_FROM = 'from'
LTRANS_TO = 'to'
LTRANS_TEXT = 'text'

LAWARD_TITLE = '<b>📯 awards board</b>'

TOPT_FULL = '(full)'
TOPT_TICKETS_TOTAL = 'tickets tpool'
TOPT_BANKRUPT = 'bankrupt'

P_BASE_PRICE = 'base price (17 march 2025)'
P_ADJUSTED_PRICE = 'adjusted price'
P_INFLATION = 'inflation'
P_FLUCTUATION = 'fluctuation'

INFM_PERSONAL_INFO = '🪪 personal info'
INFM_FIRST_NAME = 'first name'
INFM_LAST_NAME = 'last name'
INFM_USERNAME = 'username'
INFM_JOBS = '💼 jobs'
INFM_COLLECTION = '💎 collection'
INFM_ARTIFACTS = 'artifacts'
INFM_AWARDS = 'awards'
INFM_ASSETS = '💳 assets'
INFM_PERSONAL = 'personal account'
INFM_BUSINESS = 'business account'
INFM_TRANS_AVAILABLE = 'transactions available'
INFM_TBOX_AVAILABLE = 'tboxes available'

AWARD_PAYMENT = 'payment'
AWARD_ISSUED = 'issue date'
AWARD_STORY = 'story'

HIRE_JOBS = 'jobs of the member'

TPAY_SENDER = 'sender'
TPAY_RECEIVER = 'receiver'
TPAY_TOTAL = 'total'
TPAY_AMOUNT = 'amount'
TPAY_TAX = 'tax'
TPAY_DESCRIPTION = 'text'

RATE_RESET_TEXT = 'the ticket rate change'

PAGE_GEN_NO_AWARDS = 'you have no awards yet.. 😔'
PAGE_GEN_AWARDS = 'awards'
PAGE_GEN_PAYMENT = 'payment'
PAGE_GEN_ISSUED = 'issued'
PAGE_GEN_STORY = 'story'

TPOOL_PERSONAL = 'personal tpool'
TPOOL_BUSINESS = 'business tpool'
TPOOL_ARTIFACT = 'artifact tpool'
TPOOL_MATERIAL = 'material tpool'
TPOOL_TOTAL = 'total tpool'

SFS_ALERT_TRIGGER_RESPONSE = '_ААААА, СФС!_'
CRYING_STICKER_FILE_ID = 'CAACAgIAAxkBAAILdmgbiHhqbcRyeRFPoPZ4v5B7T-_XAAKbcAACGXLYSEUEtQbR1SvMNgQ'
SFS_UNALERT_FAILED = '❌ no sfs alert is issued right now'
SFS_ALERT_FAILED = """
*⚠️ the sfs alert is already issued!*
please, go to the shelter. the administration will protect you from sfs. trust the administration, glory to the community!
"""
SFS_UNALERT_TEXT = '_the sfs alert is cancelled 😴_'
SFS_ALERT_TEXT = """
*
‼️💀🔥 УВАГА! 🔥💀‼️
⚠️ ОГОЛОШЕНО СТАН ТРИВОГИ! ⚠️

💣 SFS У ЧАТІ!!! 💣
💣 SFS У ЧАТІ!!! 💣
💣 SFS У ЧАТІ!!! 💣

ЦЕ НЕ НАВЧАЛЬНА ТРИВОГА
ПОВТОРЮЮ, НЕ НАВЧАЛЬНА ТРИВОГА

🚨 БЕЗ ПАНІКИ! 🚨
📢 НЕ НЕХТУЙТЕ ВЛАСНОЮ БЕЗПЕКОЮ! СПУСКАЙТЕСЯ В УКРИТТЯ

😱 ТІКАЙ, ПОКИ НЕ ПОЧАЛОСЯ!!! 😱
📛 ПАМ'ЯТАЙ: ТВОЄ ПЕРШЕ “SFS” МОЖЕ СТАТИ ОСТАННІМ! 📛

🔪💀 🔥 АДМІНІСТРАЦІЯ ЧАТУ ЗАХИСТИТЬ ВАС ВІД СФС. ВІРТЕ В АДМІНІСТРАЦІЮ, СЛАВА СПІЛЬНОТІ! 🔥 💀🔪
*
"""

HELP_TEXT = """
✨ *Тікето-тяночка 🇺🇦* ✨

*Ticketo-chan* (ukrainian: Тікето-тяночка) is a Telegram bot for automating *Ticketonomics* processes.  
_Note that the bot is hosted on the developer's phone, so it may not always be available._

*Ticketonomics* is a game system based on *tickets* (in-game currency). More info and updates are available in the Telegram channel *TossaTickets* (https://t.me/+q66chy227wk5MWQy)

🪬 To join Ticketonomics, you must become part of our Community by joining the Telegram group *Spaceflight Simulator 🇺🇦* (@spaceflight\_simulator\_chat), and send the /reg command to Ticketo-chan.

*📊 Learn about participants and leaderboards*

*• Member info*: Reply to one's message with `/infm`, or provide one's username or ID: `/infm [username/id]`  
*• Check member's assets*: Reply with `/bal`, or provide one's username or ID: `/bal [username/id]`  
*• View member's awards*: Use the `/laward` command. Works the same as `/bal`  
*• View your transfer history*: Use the `/ltrans` command  
*• Ticket leaderboard*: Get the full list with `/topt`. For a trimmed list, provide a positive number, or for the anti-leaderboard, a negative number: `/topt [number]`  
*• Leaderboard by ticket share*: Similar to `/topt` but shown in percentages: `/topt % [number]`

*💳 Transfer assets*

*• Transfer tickets between members*: Reply to any message from the recipient, optionally add a description (it will be saved):  
`/tpay [amount] [description]`, or use their username/ID: `/tpay [username/id] [amount] [description]`.  
Both whole and fractional positive numbers are allowed (up to 2 digits after the dot/comma).

*✉️ Got questions?*

• Author: t.me/capri\_xj  
• GitHub: github.com/caprixj/TossaTicketsBot
"""
