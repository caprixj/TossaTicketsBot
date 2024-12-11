import copy
from enum import Enum

from aiogram.types import Message

from utilities.global_vars import GlobalVariables as GV


# [<reply>] /balance
# /list
# [<reply>] /info
# <reply> /addt <count:pint> [<description:text>]
# <reply> /delt <count:pint> [<description:text>]
# <reply> /sett <count:int> [<description:text>]


class ParamType(str, Enum):
    pint = 'param type: all positive integers. except zero'
    int = 'param type: all integers'
    text = 'param type: any string'


class Param:
    def __init__(self,name: str, param_type: ParamType, optional: bool):
        self.name = name
        self.param_type = param_type
        self.optional = optional


class CommandParserResult:
    def __init__(self,
                 params: dict = None,
                 response: str = None,
                 valid: bool = False):
        self.params = copy.deepcopy(params)
        self.response = response
        self.valid = valid


class CommandParser:
    def __init__(self, message: Message, reply_required: bool, reply_optional: bool):
        split = message.text.split(' ')
        split.pop(0)
        self.command_parts = split

        self.reply = message.reply_to_message
        self.reply_required = reply_required
        self.reply_optional = reply_optional
        self.params = list()

    def add_param(self, name: str, param_type: ParamType, optional: bool):
        self.params.append(Param(name, param_type, optional))
        return self

    async def parse(self) -> CommandParserResult:
        if self.reply_required and not self.reply_optional and self.reply is None:
            return await create_invalid_cpr(GV.NO_REPLY_TEXT)

        result_dict = {}
        for param in self.params:
            result_dict[param.name] = str()

        cpr = CommandParserResult(params=result_dict)

        for i in range(len(self.params)):
            param = self.params[i]
            if param.optional:
                if param.param_type == ParamType.text:
                    text = str()
                    for j in range(i, len(self.command_parts)):
                        text += self.command_parts[j] + ' '
                    cpr.params[param.name] = text[:-1]
                    cpr.valid = True
                    return cpr
                else:
                    pass  # error
                    # return await create_invalid_cpr(GV.WRONG_COMMAND_ARGUMENTS_TEXT)
            else:
                cpart = self.command_parts[i]
                if param.param_type == ParamType.pint:
                    if cpart.isdigit() and cpart[0] != '0':
                        if int(cpart) > 0:
                            pass
                        else:
                            pass  # error
                    else:
                        pass  # error
                elif param.param_type == ParamType.int:
                    if cpart.isdigit() and cpart[0] != '0':
                        pass
                    else:
                        pass  # error


async def create_invalid_cpr(response: str):
    return CommandParserResult(
        params=dict(),
        response=response,
        valid=False
    )
