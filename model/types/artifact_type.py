from enum import Enum


class ArtifactType(str, Enum):
    TEXT = 'text'
    PIC = 'pic'
    GIF = 'gif'
    AUDIO = 'audio'
    VIDEO = 'video'
