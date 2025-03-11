import copy
from enum import Enum

from aiogram.types import Message

from utilities.globalvars import GlobalVariables as GV


class CommandList(str, Enum):
    # for creator
    togglechat = '/togglechat'
    sql = '/sql <query:text>'
    addt = '<reply> /addt <count:pzint> [<description:text>]'
    delt = '<reply> /delt <count:pzint> [<description:text>]'
    sett = '<reply> /sett <count:int> [<description:text>]'

    # for all users
    help = '/help'
    toptall = '/toptall'
    topt = '/topt [<count:zint>]'
    bal = '[<reply>] /bal'
    infm = '[<reply>] /infm'


class CPRResponse(str, Enum):
    wrong_com_args = '❌ відхилено! помилкові аргументи'
    no_reply = '❌ відхилено! команда має бути у відповідь на повідомлення учасника групи'
    is_bot = '❌ відхилено! команда не може бути застосована до бота'
    not_creator = '❌ відхилено!'


class ParamType(str, Enum):
    pzint = 'all positive integers. except zero'
    zint = 'all integers. except zero'
    int = 'all integers'
    text = 'any string'


class Param:
    def __init__(self, name: str, param_type: ParamType, optional: bool):
        self.name = name
        self.param_type = param_type
        self.optional = optional


class CommandParserResult:
    def __init__(self,
                 params: dict = None,
                 response: CPRResponse = None,
                 valid: bool = False):
        self.params = copy.deepcopy(params)
        self.response = response
        self.valid = valid


async def _is_pzint(cp: str) -> bool:
    return cp.isdigit() and cp[0] != '0' and int(cp) > 0


async def _is_zint(cp: str) -> bool:
    return (cp.isdigit() or cp[1:].isdigit()) and cp[0] != '0'


async def _is_int(cp: str) -> bool:
    cp = cp[1:] if cp[0] == '-' else cp
    return cp.isdigit() and (len(cp) == 1 or (cp[0] != '0' and len(cp) > 1))


class CommandParser:
    def __init__(self,
                 message: Message,
                 creator_required: bool = False,
                 replied: bool = False,
                 reply_optional: bool = False):
        split = message.text.split(' ')
        split.pop(0)
        self.cparts = split

        self.message = message
        self.reply_message = message.reply_to_message
        self.creator_required = creator_required

        self.replied = replied
        self.reply_optional = reply_optional
        self.params = list()

    def add_param(self, name: str, param_type: ParamType, optional: bool = False):
        if param_type == ParamType.text:
            optional = True

        self.params.append(Param(name, param_type, optional))
        return self

    async def parse(self) -> CommandParserResult:
        # reply filter
        if self.replied and not self.reply_optional and self.reply_message is None:
            return await create_invalid_cpr(CPRResponse.no_reply)

        # bot filter
        if self.reply_message is not None and self.reply_message.from_user.is_bot:
            return await create_invalid_cpr(CPRResponse.is_bot)

        # creator permission filter
        if self.creator_required and self.message.from_user.id != GV.CREATOR_USER_ID:
            return await create_invalid_cpr(CPRResponse.not_creator)

        result_dict = {}
        for param in self.params:
            result_dict[param.name] = str()

        cpr = CommandParserResult(params=result_dict)

        # match every param with command string split (cparts)
        for i in range(len(self.params)):
            param = self.params[i]
            is_last_param = param.optional

            # handle the lack of an optional param
            # and the lack of required params in cparts
            if len(self.cparts) <= i:
                if not is_last_param:
                    return await create_invalid_cpr(CPRResponse.wrong_com_args)
                else:
                    cpr.params[param.name] = None
                    break

            cp = self.cparts[i]

            # -> text
            if param.param_type == ParamType.text:
                text = str()
                for j in range(i, len(self.cparts)):
                    text += self.cparts[j] + ' '
                # set resulting param value
                cpr.params[param.name] = text[:-1]
            # -> pzint
            elif param.param_type == ParamType.pzint:
                if not await _is_pzint(cp):
                    return await create_invalid_cpr(CPRResponse.wrong_com_args)
            # -> zint
            elif param.param_type == ParamType.zint:
                if not await _is_zint(cp):
                    return await create_invalid_cpr(CPRResponse.wrong_com_args)
            # -> int
            elif param.param_type == ParamType.int:
                if not cp.isdigit():
                    return await create_invalid_cpr(CPRResponse.wrong_com_args)
            # -> ?
            else:
                raise RuntimeError('Unexpected ParamType!')

            # set resulting param value for integer types
            if param.param_type != ParamType.text:
                cpr.params[param.name] = int(cp)

            if is_last_param:
                break

        # the command is parsed successfully
        cpr.valid = True
        return cpr


async def create_invalid_cpr(response: CPRResponse):
    return CommandParserResult(
        params=dict(),
        response=response,
        valid=False
    )
