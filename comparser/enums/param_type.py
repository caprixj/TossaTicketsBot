from enum import Enum


class ParamType(str, Enum):
    # all double
    real = 'real'

    # all double except zero
    nreal = 'nreal'

    # all positive double except zero
    pnreal = 'pnreal'

    # all integer
    int = 'int'

    # all integers except zero
    nint = 'nint'

    # all positive integers except zero
    pnint = 'pnint'

    # any string
    text = 'text'

    # @ + text (+ some rules)
    username = 'username'

    # positive integer + m/h/d
    time = 'time'
