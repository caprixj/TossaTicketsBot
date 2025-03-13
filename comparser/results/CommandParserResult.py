import copy

from comparser.Overload import Overload
from comparser.enums.CommandParserResultErrorMessages import CommandParserResultErrorMessages


class CommandParserResult:
    def __init__(self,
                 overload: Overload,
                 params: dict = None,
                 error_message: CommandParserResultErrorMessages = None,
                 valid: bool = False):
        self.overload = overload
        self.params = copy.deepcopy(params)
        self.error_message = error_message
        self.valid = valid
