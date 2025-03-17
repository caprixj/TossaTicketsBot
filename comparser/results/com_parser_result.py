import copy

from comparser.overload import Overload
from comparser.enums.cpr_messages import CommandParserResultMessages


class CommandParserResult:
    def __init__(self,
                 overload: Overload,
                 params: dict = None,
                 error_message: CommandParserResultMessages = None,
                 valid: bool = False):
        self.overload = overload
        self.params = copy.deepcopy(params)
        self.error_message = error_message
        self.valid = valid
