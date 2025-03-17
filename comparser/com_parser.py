import re

from aiogram.types import Message

import utilities.globals as glob
from comparser.overload import Overload
from comparser.results.com_parser_result import CommandParserResult
from comparser.enums.param_type import ParamType
from comparser.enums.cpr_messages import CommandParserResultMessages as cprem


async def _is_pnreal(t: str) -> bool:
    p = r'^(?!0(?:[.,]0{1,2})?$)(?:[1-9]\d*|0)(?:[.,]\d{1,2})?$'
    return bool(re.match(p, t))


async def _is_nreal(t: str) -> bool:
    p = r'^(?!-?0+(?:[.,]0{1,2})?$)-?(?:[1-9]\d*|0)(?:[.,]\d{1,2})?$'
    return bool(re.match(p, t))


async def _is_real(t: str) -> bool:
    p = r'^-?(?:[1-9]\d*|0)(?:[.,]\d{1,2})?$'
    return bool(re.match(p, t))


async def _is_pnint(t: str) -> bool:
    p = r'^[1-9]\d*$'
    return bool(re.match(p, t))


async def _is_nint(t: str) -> bool:
    p = r'^[1-9]\d*$'
    return bool(re.match(p, t))


async def _is_int(t: str) -> bool:
    p = r'^-?\d+$'
    return bool(re.match(p, t))


async def _is_username(t: str) -> bool:
    p = r'^@[A-Za-z][A-Za-z0-9_]{4,}$'
    return bool(re.match(p, t))


# async def _is_time(t: str) -> bool:
#     p = r'^(?:(?:[1-9]\d*d\s*)?(?:[1-9]|1\d|2[0-3])h\s*)?(?:(?:[1-9]|[1-5]\d|60)m\s*)?$'
#     return bool(re.match(p, t))


async def _create_invalid_cpr(error_message: cprem):
    return CommandParserResult(
        overload=Overload(),
        params=dict(),
        error_message=error_message
    )


class CommandParser:
    def __init__(self, message: Message, *overloads: Overload):
        self.tokens = message.text.split()[1:]
        self.message = message
        self.overloads: list[overloads] = list(overloads)

    def _replied(self) -> bool:
        return self.message.reply_to_message is not None

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
        # self-reply filter
        if (self._replied() and ol.self_reply_filter
                and self.message.reply_to_message.from_user.id == self.message.from_user.id):
            return await _create_invalid_cpr(cprem.self_reply)

        # reply filter (rFo)
        if not self._replied() and ol.reply_filter and not ol.reply_optional:
            return await _create_invalid_cpr(cprem.no_reply)

        # bot filter
        if (ol.reply_filter and self.message.reply_to_message
                and self.message.reply_to_message.from_user.is_bot):
            return await _create_invalid_cpr(cprem.is_bot)

        # creator permission filter
        if ol.creator_filter and self.message.from_user.id != glob.CREATOR_USER_ID:
            return await _create_invalid_cpr(cprem.not_creator)

        # token to param ratio filter
        min_param_count = len(ol.params)
        if ol.is_optioned():
            min_param_count -= 1
        if len(self.tokens) < min_param_count:
            return await _create_invalid_cpr(cprem.wrong_args)

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
                    return await _create_invalid_cpr(cprem.wrong_args)
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
            # -> real
            elif param.type == ParamType.real:
                if not await _is_real(t):
                    return await _create_invalid_cpr(cprem.wrong_args)
                cpr.params[param.name] = float(t)
            # -> nreal
            elif param.type == ParamType.nreal:
                if not await _is_nreal(t):
                    return await _create_invalid_cpr(cprem.wrong_args)
                cpr.params[param.name] = float(t)
            # -> pnreal
            elif param.type == ParamType.pnreal:
                if not await _is_pnreal(t):
                    return await _create_invalid_cpr(cprem.wrong_args)
                cpr.params[param.name] = float(t)
            # -> int
            elif param.type == ParamType.int:
                if not await _is_int(t):
                    return await _create_invalid_cpr(cprem.wrong_args)
                cpr.params[param.name] = int(t)
            # -> nint
            elif param.type == ParamType.nint:
                if not await _is_nint(t):
                    return await _create_invalid_cpr(cprem.wrong_args)
                cpr.params[param.name] = int(t)
            # -> pnint
            elif param.type == ParamType.pnint:
                if not await _is_pnint(t):
                    return await _create_invalid_cpr(cprem.wrong_args)
                cpr.params[param.name] = int(t)
            # -> username
            elif param.type == ParamType.username:
                if not await _is_username(t):
                    return await _create_invalid_cpr(cprem.wrong_args)
                cpr.params[param.name] = t[1:]
            # -> time
            # elif param.type == ParamType.time:
            #     if not await _is_time(t):
            #         return await _create_invalid_cpr(cprem.wrong_args)
            #     cpr.params[param.name] = t
            # -> ?
            else:
                raise RuntimeError('unexpected ParamType!')

            if param.optional:
                break

        cpr.valid = True
        return cpr
