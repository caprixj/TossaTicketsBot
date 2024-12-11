from enum import Enum


class RunMode(str, Enum):
    DEFAULT = 'default'
    DEV = 'dev'
    PROD = 'prod'
