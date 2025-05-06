from enum import Enum


class ArtifactType(str, Enum):
    text = 'text'
    picture = 'picture'
    gif = 'gif'
    audio = 'audio'
    video = 'video'
