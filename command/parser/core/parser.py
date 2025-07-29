from typing import List, Optional

from aiogram.types import Message

from command.parser.core.overload import CommandOverloadGroup, CommandOverload
from command.parser.results.parser_result import CommandParserResult
from resources import glob


class CommandParser:
    def __init__(self, message: Message, overload_group: CommandOverloadGroup):
        self.message = message
        self.overload_group = overload_group
        self.input_args = self._extract_args()

    def _extract_args(self) -> List[str]:
        parts = self.message.text.split(maxsplit=1)
        return parts[1].split() if len(parts) > 1 else []

    async def _validate_args(self, overload: CommandOverload) -> CommandParserResult:
        parsed_args = {}

        lia = len(self.input_args)
        los = len(overload.schema)

        if lia < los:
            return CommandParserResult(valid=False)

        joined_args = [
            *self.input_args[:los - 1],
            ' '.join(self.input_args[los - 1:])
        ] if lia > los else self.input_args

        for (arg_name, arg_type), value in zip(overload.schema.items(), joined_args):
            try:
                parsed_args[arg_name] = await arg_type(value).cast()
            except ValueError:
                return CommandParserResult(valid=False)

        return CommandParserResult(
            valid=True,
            message=self.message,
            overload=overload,
            args=parsed_args
        )

    async def parse(self) -> Optional[CommandParserResult]:
        if self.overload_group.is_empty():
            raise RuntimeError(glob.NO_OVERLOADS_ERROR)

        sorted_overloads = sorted(
            self.overload_group.overloads,
            key=lambda o: o.get_order_value(),
            reverse=True
        )

        for i, overload in enumerate(sorted_overloads):
            cpr = await self._parse_overload(overload)

            if cpr.fulfilled():
                return cpr

            if i == len(self.overload_group.overloads) - 1:
                return cpr

    async def _parse_overload(self, overload: CommandOverload) -> CommandParserResult:
        from_user = self.message.from_user
        reply_to_message = self.message.reply_to_message

        if from_user.is_bot or (reply_to_message and reply_to_message.from_user.is_bot):
            return CommandParserResult(bot_violation=True)

        if overload.private:
            if self.message.chat.type != 'private':
                if self.overload_group.private:
                    return CommandParserResult(private_violation=True)
                return CommandParserResult(valid=False)

        if overload.public:
            if self.message.chat.type not in ['group', 'supergroup']:
                if self.overload_group.public:
                    return CommandParserResult(public_violation=True)
                return CommandParserResult(valid=False)

        if overload.creator:
            if self.message.from_user.id != glob.CREATOR_USER_ID:
                if self.overload_group.creator:
                    return CommandParserResult(creator_violation=True)
                return CommandParserResult(valid=False)

        if overload.no_self_reply:
            if self._replied() and self.message.reply_to_message.from_user.id == self.message.from_user.id:
                return CommandParserResult(valid=False)

        if overload.reply:
            if self.message.reply_to_message is None:
                return CommandParserResult(valid=False)

        return await self._validate_args(overload)

    def _replied(self) -> bool:
        return self.message.reply_to_message is not None
