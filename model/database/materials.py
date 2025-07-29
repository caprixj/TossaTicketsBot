from dataclasses import dataclass
from datetime import datetime

from model.types import ArtifactType
from resources.glob import DATETIME_FORMAT, ARTIFACT_AGE_MULTIPLIER, ARTIFACT_OWNER_PROFIT_RATE


class Artifact:
    def __init__(self,
                 artifact_id: int = 0,
                 creator_id: int = 0,
                 owner_id: int = 0,
                 name: str = None,
                 type_: ArtifactType = ArtifactType.TEXT,
                 investment: int = 0,
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

    # +0.2% per day
    def age_multiplier(self) -> float:
        return 1 + self.age() * ARTIFACT_AGE_MULTIPLIER

    # неповні дні
    def age(self) -> int:
        return 1 + (datetime.now() - self.created_date).days

    def get_owner_profit(self) -> int:
        return round(ARTIFACT_OWNER_PROFIT_RATE * self.investment)


class MemberMaterial:
    def __init__(self,
                 user_id: int = 0,
                 material_name: str = None,
                 quantity: int = 0):
        self.user_id = user_id
        self.material_name = material_name
        self.quantity = quantity


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
