from comparser.enums.ParamType import ParamType


class Param:
    def __init__(self, name: str, type_: ParamType, optional: bool):
        self.name = name
        self.type = type_
        self.optional = optional
