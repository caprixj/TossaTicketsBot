from enum import Enum


class ParamType(str, Enum):
    int = 'all integers'
    zint = 'all integers except zero'
    pzint = 'all positive integers except zero'
    text = 'any string'
    username = '@ + text'
    time = 'positive integer + h/d'
