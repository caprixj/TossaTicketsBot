import copy

from comparser.overload import Overload


class CommandParserResult:
    def __init__(self,
                 overload: Overload,
                 params: dict = None,
                 creator_filter_violation: bool = False,
                 valid: bool = False):
        self.overload = overload
        self.params = copy.deepcopy(params)
        self.creator_filter_violation = creator_filter_violation
        self.valid = valid
