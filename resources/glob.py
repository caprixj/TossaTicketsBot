from model.types.run_mode import RunModeSettings

# RunModeSettings | defined in main.py | stored in config.xml
# bot-token, group-chat-id, db-backup-chat-id, db-file-path
rms: RunModeSettings = RunModeSettings()

CONFIG_PATH_DEV = 'config/config.xml'
CONFIG_PATH_PROD = '../config/config.xml'

UTC_FORMAT = '%Y-%m-%dT%H:%M:%SZ'
UI_DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'
DATE_FORMAT = '%Y-%m-%d'

NBT_SQL_VAR = 'nbt'
NBT_ID = -1

MSELL_TAX = 0.4
MSEND_TAX = 0.04
SINGLE_TAX = 0.07           # F
MIN_SINGLE_TAX = 0.1 * 100  # M

INFL_ALPHA = 0.9
FLUCT_GAUSS_SIGMA = 0.009
MAX_FLUCT = 1.1
MIN_FLUCT = 0.9
INIT_TPOOL = 4400.0  # ~ for 2025-05-13

PAGE_ROW_CHAR_LIMIT = 25
PAGE_ROWS_COUNT_LIMIT = 40

CHOOSE_MAT_BTN_ROW_LIMIT = 3
CHOOSE_MAT_ITEMS_LIMIT = 30

GEM_BASE_PRICE = 0.2972122 * 100
MIN_DELTA_GEM_RATE = 0.5
MAX_DELTA_GEM_RATE = 2.0
MAT_RANK_UPVAL = 1.05
MAT_RANK_DEVAL = 0.8

GEM_FREQ_SIGMA = 0.4
MIN_GEM_COUNT_TBOX = 5
MAX_GEM_COUNT_TBOX = 25

ARTIFACT_AGE_MULTIPLIER = 0.002
ARTIFACT_OWNER_PROFIT_RATE = 0.01
MIN_ARTIFACT_INIT_INVEST = 10 * 100

TG_MSG_LEN_LIMIT = 4096

TPAY_AVAILABLE_LIMIT = 10

ARTIFACT_PROFIT_YAML_PATH = 'model/yaml/artifact_profit.yaml'
GEM_FREQ_YAML_PATH = 'model/yaml/gem_freq.yaml'
MATERIALS_YAML_PATH = 'model/yaml/materials.yaml'
RECIPES_YAML_PATH = 'model/yaml/recipes.yaml'

BAN_FLAG = 'ban-flag'
ID_FLAG = 'id-flag'
PERCENT_FLAG = 'percent-flag'
TICKETS_ARG = 'tickets'
DESCRIPTION_ARG = 'description'
USERNAME_ARG = 'username'
USER_ID_ARG = 'user_id'
CHAT_ID_ARG = 'chat_id'
QUERY_ARG = 'query'
MESSAGE_ARG = 'page_message'
SIZE_ARG = 'size'
AWARD_ID_ARG = 'award_id'
PAGE_ARG = 'page'
PRICE_ARG = 'price'
EMPLOYEE_ARG = 'employee_position'
ORDER_CODE_ARG = 'order_code'

DECORATIVE_KEYBOARD_BUTTON = 'decorative:o:'

TBOX_OPEN_CALLBACK = 'tbox:open:'
ORDER_SEE_DETAILS_CALLBACK = 'order:see:'
ORDER_ACCEPT_CALLBACK = 'order:see-yes:'
ORDER_REJECT_CALLBACK = 'order:see-no:'
ORDER_ACCEPT_YES_CALLBACK = 'order:accept-yes:'
ORDER_ACCEPT_NO_CALLBACK = 'order:accept-no:'
HIDE_CALLBACK = 'hide:o:'
TPAY_YES_CALLBACK = 'tpay:yes:'
TPAY_NO_CALLBACK = 'tpay:no:'
TPAY_FEE_INCORPORATION_CALLBACK = 'tpay:fi:'
MSELL_QUANTITY_CALLBACK = 'msell:quantity:'
MSELL_YES_CALLBACK = 'msell:yes:'
MSELL_NO_CALLBACK = 'msell:no:'
MSEND_TRANSFER_CALLBACK = 'msend:transfer:'
MSEND_QUANTITY_CALLBACK = 'msend:quantity:'
MSEND_YES_CALLBACK = 'msend:yes:'
MSEND_NO_CALLBACK = 'msend:no:'
MINVO_ABORT = 'minvo:abort:'
PV_BACK_CALLBACK = 'pv:back:'
PV_FORWARD_CALLBACK = 'pv:forward:'
PV_HIDE_CALLBACK = 'pv:hide:'

INVALID_ARGS = 'THE PROGRAM WAS STARTED WITH INVALID COMMAND ARGUMENTS!'
NO_OVERLOADS_ERROR = 'PARSING WITHOUT OVERLOADS IN COMMAND PARSER!'
DOUBLE_TARGETING_ERROR = 'TRYING TO PUT TWO TARGET-TYPED ARGUMENTS INTO COMMAND OVERLOAD!'
CREATOR_VIOLATION = 'CREATOR_VIOLATION'

CONTINUE_BTN = '✅ continue'
CANCEL_BTN = '❌ cancel'
ACCEPT_BTN = '✅ accept'
REJECT_BTN = '❌ reject'
INCORPORATE_FEE_BTN = '➕ tax inside'
HIDE_BTN = '🗑 hide'
OPEN_TBOX_BTN = '➡️ open!'
ABORT_BTN = '🔄 abort'

DAILY_SCHEDULE_DONE = 'ℹ️ updated!'
TBOX_RESET_DONE  = '🎁 tbox updated!'
ADDT_TEXT = '📈 tickets added!'
DELT_TEXT = '📉 tickets removed!'
SETT_TEXT = '🔄 tickets reset!'
TPAY_TEXT = '🔀 tickets transferred!'
MSELL_TEXT = (f'*- - - - -   mSell 💱    - - - - -*'
              f'\n\n📦 choose material to sell to the national bank of ticketonomics'
              f'\n\nℹ️ the limit is {CHOOSE_MAT_ITEMS_LIMIT} items per day'
              f'\n_material amount (-reserved)_')
MSEND_TEXT = (f'*- - - - -    mSend 〽️    - - - - -*'
              f'\n\n📦 choose material to sell on the market'
              f'\n_material amount (-reserved)_')
AWARD_SUCCESS = '🎖 the member has been awarded!'
REG_SUCCESS = '🎉 successfully signed up!\nwelcome to ticketonomics'
UNREG_TEXT = '☠️ mercilessly kicked out of ticketonomics'
RUSNI_TEXT = 'пизда!'
TOPT_DESC = '*💸 tickets leaderboard*'
TOPT_ASC = '*💩 tickets anti-leaderboard*'
TOPM_DESC = '*📦🔝 materials leaderboard*'
TOPM_ASC = '*📦💩 materials anti-leaderboard*'
INFM_TEXT = '<b>ℹ️ member information</b>'
TBOX_TEXT = '🎁 daily tbox'
TAG_TEXT = 'click to see the account'
TBOX_OPENED_TEXT = 'your tbox reward'
ANCHOR_SUCCESS = '✅⚓️ successfully changed the native chat'
SQL_SUCCESS = '✅ command executed!'
MEMBER_HIRED = '✅💼 member hired for the position!'
RESET_PRICE_COMMAND_DONE = '✅ manual price reset executed based on the ticket inflation rate'
MEMBER_ALREADY_HIRED = '⚠️ member already holds this position!'
MEMBER_FIRED = '💢💼 member has been fired!'
DELETED_MEMBER = '[deleted]'
NOT_IMPLEMENTED = 'not implemented yet :('
ALERT_CALLBACK_YES = 'you cannot confirm this action!'
ALERT_CALLBACK_NO = 'you cannot cancel this action!'
ALERT_CALLBACK_ACTION = 'you cannot perform this action!'
CALLBACK_FLOOD_CONTROL = 'not so fast! at this rate, telegram will send ticketo-chan to hell.. (wait at least 20 seconds)'
CALLBACK_EXPIRED = 'this button is too old :('
FLOW_CANCELED = '✅ canceled'

NOTHING_TO_CANCEL = '🥀'

PUBLIC_VIOLATION = '⚠️ this command can be used only in groups'
PRIVATE_VIOLATION = "⚠️ this command can be used only in bot's private messages"
AWARD_DUPLICATE = '⚠️ participant already has this award!'
REG_DENIED_CTT_NONE = '⚠️ you are already a member of ticketonomics!'
REG_DENIED_CTT_REPLY = '⚠️ this participant is already part of ticketonomics!'
SQL_FAILED = '❌ command rejected!'
COM_PARSER_FAILED = '❌ invalid command!'
TG_MSG_LEN_LIMIT_ERROR = '⚠️ the result is too long for a telegram message'
TARGET_NOT_MEMBER_ERROR = '❌ the specified user is not a ticketonomics member!'
GET_MEMBER_FAILED = '❌ member not found! check the id you entered'
SENDER_NO_LONGER_EXISTS = '❌ you are no longer a ticketonomics member! operation was cancelled'
RECEIVER_NO_LONGER_EXISTS = '❌ receiver no longer exists! operation was cancelled'
GET_AWARD_FAILED = '❌ specified award does not exist! check the id you entered'
SERVICE_OPERATION_NONE_RESULT = '😔 couldn’t complete the operation..'
NOT_MEMBER_ERROR = '⚠️ to use the bot, you must be a member of the sfs chat and send the /reg command. more instructions can be found at /help'
TBOX_UNAVAILABLE_ERROR = '❌ you already opened a tbox today!'
TPAY_UNAVAILABLE_ERROR = '❌ rejected! daily transaction limit reached'
MSELL_QUANTITY_INVALID = '❌ invalid quantity'
MSEND_QUANTITY_INVALID = '❌ invalid quantity'
MSEND_TRANSFER_INVALID = '❌ invalid amount'
MSEND_QUANTITY_INSUFFICIENT = '❌ rejected! not enough material'
MSELL_ITEMS_LIMIT_REACHED = "❌ too much! consider the limit. *sell cancelled*"
ORDER_NOT_FOUND = '❌ order not found'
SENDER_NOT_FOUND = '❌ sender not found'
RECEIVER_NOT_FOUND = '❌ receiver not found'
MATERIAL_NOT_FOUND = '❌ sender does not have this sort of material anymore'
NOT_ENOUGH_MATERIAL = '❌ sender does not have enough material anymore'
RESERVATION_VIOLATED = '❌ not enough material. sender has some in reserve for someone else!'
UNKNOWN_ENUM = '❌ unknown enum returned'
ORDER_FORBIDDEN = "❌ forbidden! you cannot see someone else's order details"
USE_MINVO_INSTEAD = '⚠️ to see details of an order you made, use  `/minvo <order-code>`'
SELF_TRANS_ERROR = '❌ you cannot tpay yourself'
SELF_MSEND_ERROR = '❌ you cannot sell materials to yourself'
NOT_TXT_FILE_ERROR = "❌ it's not a text file"
MEMBER_ALREADY_FIRED = '❌ cannot fire member as he does not hold this position!'
ANCHOR_REJECTED = "❌⚓️ you're already anchored here!"
UNREG_CREATOR_ERROR = "i won't kill you, my lord! ♥️"
FLOW_EXPIRED = '⚠️ expired'

MEMBER_RES = 'member'
POSITION_RES = 'position'
AMOUNT_RES = 'amount'

BAL_NAME = "🪪 name"
BAL_PERSONAL = '💳 personal account'
BAL_BUSINESS = '💸 business account'
BAL_TPAY_AVAILABLE = '🔀 tpay available'
BAL_TBOX_AVAILABLE = '🎁 tbox available'

BALM_BALANCE_EMPTY = 'you have no materials yet.. 😶‍🌫️'
BALM_NO_GEMSTONES = 'you have no gemstones yet.. 😶‍🌫️'
BALM_NO_INTERMEDIATES = 'you have no intermediates yet.. 😶‍🌫️'
BALM_NO_ARTIFACT_TEMPLATES = 'you have no artifact templates yet.. 😶‍🌫️'
BALM_TITLE = '📦 materials account'
BALM_QUANTITY_HINT = 'amount (-reserved)'
BALM_START_TEXT = """
page 1 - gemstones
page 2 - intermediates
page 3 - artifact templates
"""

TBOX_MEMBER = f'🪪 {MEMBER_RES}'

TXN_TITLE = '<b>📊 income and expenses history (tickets)</b>'
TXN_START_TEXT = "🔹 income | 🔻 expense"
TXN_TRANS_HISTORY_EMPTY = 'your transactions history is empty.. 😶‍🌫️'
TXN_FROM = 'from'
TXN_TO = 'to'
TXN_TEXT = 'text'

LAWARD_TITLE = '<b>📯 awards board</b>'

TOP_FULL = '(full)'
TOP_BANKRUPT = 'bankrupt'

TOPT_TICKETS_TOTAL = 'tickets total'
TOPT_TPOOL = 'tpool'

TOPM_PURE_DISCLAIMER = 'values after taxation (!)'
TOPM_PURE_MPOOL = 'pure mpool'
TOPM_TAXED_MPOOL = 'taxed mpool'

RATES_REAL_INFL = 'real inflation'
RATES_PURE_INFL = 'pure inflation'
RATES_FLUCT = 'fluctuation'

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
TPAY_TAX = 'tax'
TPAY_DESCRIPTION = 'text'

MSELL_CHOSEN_MATERIAL_EMOJI = '📦 chosen material'
MSELL_CHOSEN_MATERIAL = 'chosen material'
MSELL_ASK_QUANTITY = 'enter how many to sell'
MSELL_FIELD_PLACEHOLDER = 'for example, 73'
MSELL_MATERIALS_TO_SELL = '📄 materials to sell'
MSELL_PRICE = 'price'
MSELL_REVENUE = 'revenue'
MSELL_SINGLE_TAX_TEXT = 'single tax'
MSELL_MSELL_TAX_TEXT = 'msell tax'
MSELL_INCOME = 'income'
MSELL_YES = '✅ sold for'
MSELL_NO = '✖️ sell cancelled'

MSEND_CHOSEN_MATERIAL_EMOJI = '📦 chosen material'
MSEND_SENDER = 'sender'
MSEND_RECEIVER = 'receiver'
MSEND_YOU_SEND = 'you send'
MSEND_ASK_QUANTITY = '🔢 enter how many to sell'
MSEND_ASK_TRANSFER = '💵 enter offered cost (how much the buyer pays)'
MSEND_MAT_ORDER = '📄 order'
MSEND_TO_SELL = 'to sell'
MSEND_RATE_PRICE = 'rate price'
MSEND_YOUR_PRICE = 'your price'
MSEND_YOU_RECEIVE = 'you receive'
MSEND_BUYER_PAYS = 'buyer pays'
MSEND_SINGLE_TAX_TEXT = 'single tax'
MSEND_MSEND_TAX_TEXT = 'msend tax'
MSEND_DESCRIPTION = 'text'
MSEND_YES = '✅ order sent'
MSEND_CODE = 'order code'
MSEND_COPY = '(tap or hold to copy)'
MSEND_RECEIVER_NOTIFIED_SUCCESS = '✅ receiver is notified'
MSEND_RECEIVER_NOTIFIED_FAILED = '⚠️ receiver cannot be reached to get notified'
MSEND_SENDER_NOTIFIED_SUCCESS = 'ℹ️ sender is notified'
MSEND_SENDER_NOTIFIED_FAILED = '⚠️ sender cannot be reached to get notified'
MSEND_YES_HINT = ('ℹ️ important:'
                  '\n1) you can share the order code with anyone but only you and your buyer will be able to see details, cancel or accept it'
                  '\n2) sudden tax changes might affect the total cost of the deal!'
                  '\n3) use <code>/minvo</code> to see all your active invoices (deals you offered)'
                  '\n4) use <code>/minvo code</code>, to see relevant details or cancel the order')
MSEND_NO = '✖️ order cancelled'
MSEND_RECEIVER_NOTIFICATION = '🆕 incoming trade offer'
MSEND_SEE_DETAILS_BTN = '➡️ see details'
MSEND_ACCEPT_CONFIRM = '❓ confirm you want to accept the deal. it cannot be aborted'
MSEND_ACCEPTED = '✅ deal completed'
MSEND_ACCEPT_NO = 'ℹ️ canceled. you still can accept the deal later'
MSEND_REJECTED = '🔙 deal rejected!'

RATE_RESET_TEXT = 'ℹ️ inflation'

PAGE_GEN_NO_AWARDS = 'you have no awards yet.. 😔'
PAGE_GEN_AWARDS = 'awards'
PAGE_GEN_PAYMENT = 'payment'
PAGE_GEN_ISSUED = 'issued'
PAGE_GEN_STORY = 'story'

TPOOL_NBT = 'national bank'
TPOOL_PERSONAL = 'personal accounts'
TPOOL_BUSINESS = 'business accounts'
TPOOL_ARTIFACT = 'artifacts'
TPOOL_MATERIAL = 'materials'
TPOOL_TOTAL = 'tpool'

MOFFER_OFFER = '(offer)'
MOFFER_TITLE = '*📩〽️ incoming trade deals*\n(material orders)'
MOFFER_MEMBER = 'member'
MOFFER_EMPTY = 'you have no incoming trade deals.. 😶‍🌫️'
MOFFER_FROM = 'from'
MOFFER_COST = 'cost'
MOFFER_TEXT = 'text'
MOFFER_MAT_ORDER = '📄 order'
MOFFER_SENDER = 'sender'
MOFFER_RECEIVER = 'receiver'
MOFFER_YOU_PAY = 'you pay'
MOFFER_YOU_RECEIVE = 'you receive'
MOFFER_OFFERED_TO_PAY = 'offered to pay'
MOFFER_SINGLE_TAX_TEXT = 'single tax'
MOFFER_MSEND_TAX_TEXT = 'msend tax'
MOFFER_RATE_PRICE = 'rate price'
MOFFER_OFFERED_PRICE = 'offered price'
MOFFER_DESCRIPTION = 'text'

MINVO_INVOICE = '(invoice)'
MINVO_TITLE = '*📤〽️ outcoming trade deals *\n(material orders)'
MINVO_MEMBER = 'member'
MINVO_EMPTY = 'you have no outcoming trade deals.. 😶‍🌫️'
MINVO_TO = 'to'
MINVO_COST = 'cost'
MINVO_TAX_TEXT = 'tax'
MINVO_TEXT = 'text'
MINVO_SENDER = 'sender'
MINVO_RECEIVER = 'receiver'
MINVO_YOU_SEND = 'you send'
MINVO_YOU_RECEIVE = 'you receive'
MINVO_MAT_ORDER = '📄 order'
MINVO_TO_SELL = 'to sell'
MINVO_RATE_PRICE = 'rate price'
MINVO_YOUR_PRICE = 'your price'
MINVO_BUYER_PAYS = 'buyer pays'
MINVO_SINGLE_TAX_TEXT = 'single tax'
MINVO_MSEND_TAX_TEXT = 'msend tax'
MINVO_DESCRIPTION = 'text'
MINVO_ABORTED = '🔄 deal aborted'

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

START_TEXT = """
*Ticketo-chan* (ukrainian: Тікето-тяночка) is the main bot of *Ticketonomics*! The platform for games and role-playing based on *tickets* (bot's currency)

More information, updates and news available in *TossaTickets* (https://t.me/+q66chy227wk5MWQy)

To join Ticketonomics, you must become part of our Community by joining one of our groups
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
