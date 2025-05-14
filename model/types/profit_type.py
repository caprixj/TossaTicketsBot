from enum import Enum


class ProfitType(str, Enum):
    unknown = 'unknown'
    artifact_creator = 'artifact_creator'
    artifact_owner = 'artifact_owner'
