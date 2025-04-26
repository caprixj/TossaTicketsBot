from typing import Type, List

from model.types.ticketonomics_types import TicketonomicsType, Username, UserID, PercentSpecialArgument
from command.parser.types.target_type import CommandTargetType as CTT
from resources.const import glob


class CommandOverload:
    def __init__(self,
                 oid: str = None,
                 creator_required: bool = False,
                 reply_required: bool = False,
                 no_self_reply_required: bool = False):
        self.oid = oid
        self.creator_required = creator_required
        self.reply_required = reply_required
        self.no_self_reply_required = no_self_reply_required
        self.schema = {}
        self.target_type = CTT.reply if reply_required else CTT.none

    def add(self, name: str, arg_type: Type[TicketonomicsType]):
        if arg_type == Username:
            if self.target_type != CTT.none:
                raise RuntimeError(glob.DOUBLE_TARGETING_ERROR)
            else:
                self.target_type = CTT.username

        if arg_type == UserID:
            if self.target_type != CTT.none:
                raise RuntimeError(glob.DOUBLE_TARGETING_ERROR)
            else:
                self.target_type = CTT.user_id

        self.schema[name] = arg_type
        return self

    def add_percent(self):
        self.schema[glob.PERCENT_ARG] = PercentSpecialArgument
        return self

    def get_order_value(self) -> int:
        v = 2 * len(self.schema)
        return v + 1 if self.reply_required else v


class CommandOverloadGroup:
    def __init__(self,
                 overloads: List[CommandOverload],
                 creator_required: bool = False):
        self.overloads = overloads
        self.creator_required = creator_required

        if self.creator_required:
            for o in overloads:
                o.creator_required = True
        else:
            self.creator_required = True
            for o in overloads:
                if not o.creator_required:
                    self.creator_required = False
                    break

    def __iter__(self):
        return iter(self.overloads)

    def __getitem__(self, index: int) -> CommandOverload:
        return self.overloads[index]

    def is_empty(self) -> bool:
        return not self.overloads
