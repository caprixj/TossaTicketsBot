from comparser.param import Param
from comparser.enums.overload_type import OverloadType
from comparser.enums.param_type import ParamType


class Overload:
    def __init__(self,
                 name: str = None,
                 type_: OverloadType = OverloadType.none,
                 creator_filter: bool = False,
                 reply_filter: bool = False,
                 self_reply_filter: bool = False,
                 reply_optional: bool = False):
        self.name = name
        self.type = type_
        self.creator_filter = creator_filter
        self.reply_filter = reply_filter
        self.self_reply_filter = self_reply_filter
        self.reply_optional = reply_optional
        self.params: list[Param] = list()

    def add_param(self, name: str, type_: ParamType, optional: bool = False):
        if self.is_optioned():
            raise RuntimeError('trying to add two optional params to an overload')

        if type_ == ParamType.text:
            optional = True

        self.params.append(Param(name, type_, optional))
        return self

    def is_optioned(self):
        return self.params and self.params[-1].optional

    def get_order_value(self, replied: bool) -> int:
        # param: +100
        # optional param: +10
        # RFo || rFo: +3
        # RFO || rfo: +2
        # Rfo || rFO: +1

        r = replied
        f = self.reply_filter
        o = self.reply_optional

        v = 3 if (f and not o) else 1 if (r ^ f & o) else 2

        if self.params:
            v += 100 * len(self.params)

        if self.is_optioned():
            v -= 90

        return v
