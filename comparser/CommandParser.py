from aiogram.types import Message

import utilities.globals as glob
from comparser.Overload import Overload
from comparser.results.CommandParserResult import CommandParserResult
from comparser.enums.ParamType import ParamType
from comparser.enums.ResultErrorMessages import ResultErrorMessages


async def _is_pzint(t: str) -> bool:
    return t.isdigit() and t[0] != '0' and int(t) > 0


async def _is_zint(t: str) -> bool:
    return (t.isdigit() or t[1:].isdigit()) and t[0] != '0'


async def _is_int(t: str) -> bool:
    t = t[1:] if t[0] == '-' else t
    return t.isdigit() and (len(t) == 1 or (t[0] != '0' and len(t) > 1))


async def _is_username(t: str) -> bool:
    if t[0] != '@' or t[1].isdigit():
        return False

    for char in t[1:]:
        if not (char.isalnum() or char == '_'):
            return False

    return True


async def _is_time(t: str) -> bool:
    return t[-1] in ['m', 'h', 'd'] and t[:-1].isdigit()


async def _create_invalid_cpr(error_message: ResultErrorMessages):
    return CommandParserResult(
        overload=Overload(),
        params=dict(),
        error_message=error_message
    )


class CommandParser:
    def __init__(self, message: Message, *overloads: Overload):
        self.tokens = message.text.split()[1:]
        self.message = message
        self.reply_message = message.reply_to_message
        self.overloads: list[overloads] = list(overloads)

    def _replied(self) -> bool:
        return self.reply_message is not None

    async def parse(self) -> CommandParserResult:
        if not self.overloads:
            return CommandParserResult(
                overload=Overload(name=str()),
                params=dict()
            )

        sorted_overloads = sorted(
            self.overloads,
            key=lambda o: o.get_order_value(self._replied()),
            reverse=True
        )

        for i, ol in enumerate(sorted_overloads):
            cpr = await self._parse_overload(ol)
            if cpr.valid:
                return cpr
            if i == len(self.overloads) - 1:
                return cpr

    async def _parse_overload(self, ol: Overload):
        # reply filter (rFo)
        if not self._replied() and ol.reply_filter and not ol.reply_optional:
            return await _create_invalid_cpr(ResultErrorMessages.no_reply)

        # bot filter
        if ol.reply_filter and self.reply_message and self.reply_message.from_user.is_bot:
            return await _create_invalid_cpr(ResultErrorMessages.is_bot)

        # creator permission filter
        if ol.creator_filter and self.message.from_user.id != glob.CREATOR_USER_ID:
            return await _create_invalid_cpr(ResultErrorMessages.not_creator)

        # token to param ratio filter
        min_param_count = len(ol.params)
        if ol.is_optioned():
            min_param_count -= 1
        if len(self.tokens) < min_param_count:
            return await _create_invalid_cpr(ResultErrorMessages.wrong_args)

        result_dict = dict()
        for param in ol.params:
            result_dict[param.name] = str()

        cpr = CommandParserResult(overload=ol, params=result_dict)

        # match every param with command string split (tokens)
        for i, param in enumerate(ol.params):
            # handle the lack of an optional param
            # and the lack of required params in tokens
            if len(self.tokens) <= i:
                if not param.optional:
                    return await _create_invalid_cpr(ResultErrorMessages.wrong_args)
                else:
                    cpr.params[param.name] = None
                    break

            t = self.tokens[i]

            # -> text
            if param.type == ParamType.text:
                text = str()
                for j in range(i, len(self.tokens)):
                    text += self.tokens[j] + ' '
                # set resulting param value
                cpr.params[param.name] = text[:-1]
            # -> int
            elif param.type == ParamType.int:
                if not t.isdigit():
                    return await _create_invalid_cpr(ResultErrorMessages.wrong_args)
                cpr.params[param.name] = int(t)
            # -> zint
            elif param.type == ParamType.zint:
                if not await _is_zint(t):
                    return await _create_invalid_cpr(ResultErrorMessages.wrong_args)
                cpr.params[param.name] = int(t)
            # -> pzint
            elif param.type == ParamType.pzint:
                if not await _is_pzint(t):
                    return await _create_invalid_cpr(ResultErrorMessages.wrong_args)
                cpr.params[param.name] = int(t)
            # -> username
            elif param.type == ParamType.username:
                if not await _is_username(t):
                    return await _create_invalid_cpr(ResultErrorMessages.wrong_args)
                cpr.params[param.name] = t[1:]
            # -> time
            elif param.type == ParamType.time:
                if not await _is_time(t):
                    return await _create_invalid_cpr(ResultErrorMessages.wrong_args)
                cpr.params[param.name] = t
            # -> ?
            else:
                raise RuntimeError('Unexpected ParamType!')

            if param.optional:
                break

        # if not self.tokens and ol.params:
        #     if not ol.params[-1].optional:
        #         return await _create_invalid_cpr(ResultErrorMessages.wrong_args)

        # the command overload is parsed successfully
        cpr.valid = True
        return cpr
