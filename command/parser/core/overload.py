from typing import Type, List

from model.types.custom.flags import Flag
from model.types.custom.primitives import TicketonomicsType, Username, UserID
from command.parser.types.target_type import CommandTargetType as CTT
from resources import glob
from utils import funcs


class CommandOverload:
    def __init__(self,
                 oid: str = None,
                 otype: str = None,
                 admin: bool = False,
                 reply: bool = False,
                 no_self_reply: bool = False,
                 private: bool = False,
                 public: bool = False):
        self.oid = oid
        self.otype = otype
        self.admin = admin
        self.reply = reply
        self.no_self_reply = no_self_reply
        self.private = private
        self.public = public
        self.schema = {}
        self.target_type = CTT.REPLY if reply else CTT.NONE

    def add(self, name: str, arg_type: Type[TicketonomicsType]):
        if arg_type == Username:
            if self.target_type != CTT.NONE:
                raise RuntimeError(glob.DOUBLE_TARGETING_ERROR)
            else:
                self.target_type = CTT.USERNAME

        if arg_type == UserID:
            if self.target_type != CTT.NONE:
                raise RuntimeError(glob.DOUBLE_TARGETING_ERROR)
            else:
                self.target_type = CTT.USER_ID

        self.schema[name] = arg_type
        return self

    def flag(self, flag_type: Type[Flag]):
        self.schema[flag_type.ID] = flag_type
        return self

    def get_order_value(self) -> int:
        v = 2 * len(self.schema)
        return v + 1 if self.reply else v


class CommandOverloadGroup:
    def __init__(self,
                 overloads: List[CommandOverload],
                 admin: bool = False,
                 private: bool = False,
                 public: bool = False):
        self.overloads = overloads
        self.admin = admin
        self.private = private
        self.public = public

        forced = {
            'admin': admin,
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

        if not funcs.all_unique_or_none([o.oid for o in overloads]):
            raise RuntimeError('cog: not all oid unique!')

    def __iter__(self):
        return iter(self.overloads)

    def __getitem__(self, index: int) -> CommandOverload:
        return self.overloads[index]

    def is_empty(self) -> bool:
        return not self.overloads
