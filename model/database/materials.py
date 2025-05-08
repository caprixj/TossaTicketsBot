from dataclasses import dataclass
from datetime import datetime

from model.types import ArtifactType
from resources.const.glob import DATETIME_FORMAT


class Artifact:
    def __init__(self,
                 artifact_id: int = 0,
                 creator_id: int = 0,
                 owner_id: int = 0,
                 name: str = None,
                 type_: ArtifactType = ArtifactType.text,
                 investment: float = 0.0,
                 file_id: str = None,
                 description: str = None,
                 created_date: str = None):
        self.artifact_id = artifact_id
        self.creator_id = creator_id
        self.owner_id = owner_id
        self.name = name
        self.type_ = type_
        self.investment = investment
        self.file_id = file_id
        self.description = description
        self.created_date = datetime.strptime(created_date, DATETIME_FORMAT)

    # def get_destroy_refund(self) -> float:
    #     days_passed = (datetime.now() - self.created_date).days
    #     time_fine = max((100 - days_passed / 2) / 100, 0)
    #     return round(self.investment * time_fine, 2)


@dataclass
class Material:
    name: str
    emoji: str


@dataclass
class Ingredient:
    name: str
    quantity: int


@dataclass
class Recipe:
    result: Ingredient
    ingredients: list[Ingredient]
