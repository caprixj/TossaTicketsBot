from typing import Type, List

from model.types.ticketonomics_types import TicketonomicsType, Username, UserID, PercentSpecialArgument, \
    IdSpecialArgument
from command.parser.types.target_type import CommandTargetType as ctt
from resources.const import glob


class CommandOverload:
    def __init__(self,
                 oid: str = None,
                 creator: bool = False,
                 reply: bool = False,
                 no_self_reply: bool = False,
                 private: bool = False,
                 public: bool = False):
        self.oid = oid
        self.creator = creator
        self.reply = reply
        self.no_self_reply = no_self_reply
        self.private = private
        self.public = public
        self.schema = {}
        self.target_type = ctt.reply if reply else ctt.none

    def add(self, name: str, arg_type: Type[TicketonomicsType]):
        if arg_type == Username:
            if self.target_type != ctt.none:
                raise RuntimeError(glob.DOUBLE_TARGETING_ERROR)
            else:
                self.target_type = ctt.username

        if arg_type == UserID:
            if self.target_type != ctt.none:
                raise RuntimeError(glob.DOUBLE_TARGETING_ERROR)
            else:
                self.target_type = ctt.user_id

        self.schema[name] = arg_type
        return self

    def add_percent(self):
        self.schema[glob.PERCENT_ARG] = PercentSpecialArgument
        return self

    def add_id(self):
        self.schema[glob.ID_ARG] = IdSpecialArgument
        return self

    def get_order_value(self) -> int:
        v = 2 * len(self.schema)
        return v + 1 if self.reply else v


class CommandOverloadGroup:
    def __init__(self,
                 overloads: List[CommandOverload],
                 creator: bool = False,
                 private: bool = False,
                 public: bool = False):
        self.overloads = overloads
        self.creator = creator
        self.private = private
        self.public = public

        forced = {
            'creator': creator,
            'private': private,
            'public': public,
        }

        for name, is_forced in forced.items():
            if is_forced:
                setattr(self, name, True)
                for o in overloads:
                    setattr(o, name, True)
            else:
                all_on = all(getattr(o, name) for o in overloads)
                setattr(self, name, all_on)

    def __iter__(self):
        return iter(self.overloads)

    def __getitem__(self, index: int) -> CommandOverload:
        return self.overloads[index]

    def is_empty(self) -> bool:
        return not self.overloads
