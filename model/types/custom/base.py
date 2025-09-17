class TicketonomicsType:
    def __init__(self, data: str):
        self.data = data

    async def cast(self):
        return self.data


def eufloat(value: str):
    if isinstance(value, str):
        value = value.replace(",", ".")
    return float(value)
