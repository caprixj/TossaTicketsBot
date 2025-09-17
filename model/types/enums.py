from enum import Enum


class ArtifactType(str, Enum):
    TEXT = 'text'
    PIC = 'pic'
    GIF = 'gif'
    AUDIO = 'audio'
    VIDEO = 'video'


class GemCountingMode(str, Enum):
    PRICING = 'pricing'
    RATES = 'rates'


class OrderingType(str, Enum):
    DESC = 'DESC'
    ASC = 'ASC'


class ProductType(str, Enum):
    UNKNOWN = 'unknown'
    GEMSTONE = 'gemstone'
    CRAFT = 'craft'
    SERVICE = 'service'


class ProfitType(str, Enum):
    UNKNOWN = 'unknown'
    ARTIFACT_CREATOR = 'artifact_creator'
    ARTIFACT_OWNER = 'artifact_owner'


class RunMode(str, Enum):
    DEFAULT = 'default'
    DEV = 'dev'
    PROD = 'prod'


class TransactionResultErrors(str, Enum):
    INSUFFICIENT_FUNDS = '❌ rejected! insufficient funds'
    TPAY_UNAVAILABLE = '❌ rejected! daily transaction limit reached'


class TicketTxnType(str, Enum):
    UNKNOWN = 'unknown'
    ADMIN = 'admin'
    UNREG = 'unreg'
    TPAY = 'tpay'
    MSELL = 'msell'
    MSEND = 'msend'
    AWARD = 'award'
    SALARY = 'salary'


class MaterialTxnType(str, Enum):
    UNKNOWN = 'unknown'
    TBOX = 'tbox'
    MSELL = 'msell'
    MSEND = 'msend'


class TaxType(str, Enum):
    UNKNOWN = 'unknown'
    SINGLE = 'single'
    MSELL = 'msell'
    MSEND = 'msend'


class TaxParentType(str, Enum):
    UNKNOWN = 'unknown'
    TICKET = 'ticket'
    MATERIAL = 'material'


class MaterialDealStatus(str, Enum):
    ACCEPTED = 'accepted'
    REJECTED = 'rejected'
    ABORTED = 'aborted'
    # EXPIRED = 'expired'


class MaterialDealResult(Enum):
    SUCCESS = 1
    ORDER_NOT_FOUND = 2
    SENDER_NOT_FOUND = 3
    RECEIVER_NOT_FOUND = 4
    MATERIAL_NOT_FOUND = 5
    NOT_ENOUGH_MATERIAL = 6
    RESERVATION_VIOLATED = 7
