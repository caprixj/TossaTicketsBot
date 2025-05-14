from enum import Enum


class ArtifactType(str, Enum):
    text = 'text'
    pic = 'pic'
    gif = 'gif'
    audio = 'audio'
    video = 'video'
