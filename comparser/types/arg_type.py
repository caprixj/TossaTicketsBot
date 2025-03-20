import re

# time type
# r'^(?:(?:[1-9]\d*d\s*)?(?:[1-9]|1\d|2[0-3])h\s*)?(?:(?:[1-9]|[1-5]\d|60)m\s*)?$'


def _eufloat(value: str):
    if isinstance(value, str):
        value = value.replace(",", ".")
    return float(value)


class CommandArgumentType:
    def __init__(self, data: str):
        self.data = data

    def cast(self):
        return self.data


# any string
class Text(CommandArgumentType):
    def __init__(self, data: str):
        super().__init__(data)

    def cast(self) -> str:
        return str(self.data)


# any string <= 64 chars
class Text64(CommandArgumentType):
    def __init__(self, data: str):
        super().__init__(data)

    def cast(self) -> str:
        if len(self.data) <= 64:
            return self.data
        else:
            raise ValueError()


# any string <= 256 chars
class Text256(CommandArgumentType):
    def __init__(self, data: str):
        super().__init__(data)

    def cast(self) -> str:
        if len(self.data) <= 256:
            return self.data
        else:
            raise ValueError()


# all double
class Real(CommandArgumentType):
    def __init__(self, data: str):
        super().__init__(data)
        self.pattern = r'^-?(?:[1-9]\d*|0)(?:[.,]\d{1,2})?$'

    def cast(self) -> float:
        if bool(re.match(self.pattern, self.data)):
            return float(_eufloat(self.data))
        else:
            raise ValueError()


# all double except zero
class NReal(CommandArgumentType):
    def __init__(self, data: str):
        super().__init__(data)
        self.pattern = r'^(?!-?0+(?:[.,]0{1,2})?$)-?(?:[1-9]\d*|0)(?:[.,]\d{1,2})?$'

    def cast(self) -> float:
        if bool(re.match(self.pattern, self.data)):
            return float(_eufloat(self.data))
        else:
            raise ValueError()


# all positive double except zero
class PNReal(CommandArgumentType):
    def __init__(self, data: str):
        super().__init__(data)
        self.pattern = r'^(?!0(?:[.,]0{1,2})?$)(?:[1-9]\d*|0)(?:[.,]\d{1,2})?$'

    def cast(self) -> float:
        if bool(re.match(self.pattern, self.data)):
            return float(_eufloat(self.data))
        else:
            raise ValueError()


# all integer
class Int(CommandArgumentType):
    def __init__(self, data: str):
        super().__init__(data)
        self.pattern = r'^-?\d+$'

    def cast(self) -> int:
        if bool(re.match(self.pattern, self.data)):
            return int(self.data)
        else:
            raise ValueError()


# all integer except zero
class NInt(CommandArgumentType):
    def __init__(self, data: str):
        super().__init__(data)
        self.pattern = r'^-?[1-9]\d*$'

    def cast(self) -> int:
        if bool(re.match(self.pattern, self.data)):
            return int(self.data)
        else:
            raise ValueError()


# all positive integers except zero
class PNInt(CommandArgumentType):
    def __init__(self, data: str):
        super().__init__(data)
        self.pattern = r'^[1-9]\d*$'

    def cast(self) -> int:
        if bool(re.match(self.pattern, self.data)):
            return int(self.data)
        else:
            raise ValueError()


class UserID(PNInt):
    def __init__(self, data: str):
        super().__init__(data)

    def cast(self) -> int:
        return super().cast()


# @ + text (+ some rules)
class Username(CommandArgumentType):
    def __init__(self, data: str):
        super().__init__(data)
        self.pattern = r'^@[A-Za-z_][A-Za-z0-9_]{4,}$'

    def cast(self) -> str:
        if len(self.data) <= 33 and bool(re.match(self.pattern, self.data)):
            return self.data[1:]
        else:
            raise ValueError()
