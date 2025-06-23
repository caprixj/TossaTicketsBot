from enum import Enum


class ProfitType(str, Enum):
    UNKNOWN = 'unknown'
    ARTIFACT_CREATOR = 'artifact_creator'
    ARTIFACT_OWNER = 'artifact_owner'
