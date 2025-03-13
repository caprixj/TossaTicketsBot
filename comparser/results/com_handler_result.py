from comparser.results.com_parser_result import CommandParserResult
from model.database.member import Member


class CommandHandlerResult:
    def __init__(self,
                 target_member: Member = None,
                 cpr: CommandParserResult = None,
                 valid: bool = False):
        self.target_member = target_member
        self.cpr = cpr
        self.valid = valid

    def get_param(self, param_key: str):
        return self.cpr.params.get(param_key)
