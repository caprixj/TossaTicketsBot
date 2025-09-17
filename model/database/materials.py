from dataclasses import dataclass
from datetime import datetime, timezone

from model.types.custom.primitives import OrderCode
from model.types.enums import ArtifactType, MaterialDealStatus
from utils import funcs
from resources.glob import ARTIFACT_AGE_MULTIPLIER, ARTIFACT_OWNER_PROFIT_RATE


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


class MemberMaterial:
    def __init__(self,
                 user_id: int = 0,
                 material_name: str = None,
                 quantity: int = 0):
        self.user_id = user_id
        self.material_name = material_name
        self.quantity = quantity


class MaterialOrder:
    def __init__(self,
                 code: str = None,
                 sender_id: int = 0,
                 receiver_id: int = 0,
                 material_name: str = 0,
                 quantity: int = 0,
                 offered_cost: int = 0,
                 created_at: str = None,
                 description: str = None):
        self.code: str = OrderCode(code).sync_cast()
        self.sender_id = sender_id
        self.receiver_id = receiver_id
        self.material_name = material_name
        self.quantity = quantity
        self.offered_cost = offered_cost
        self.created_at = funcs.to_utc(created_at)
        self.description = description


class MaterialDeal:
    def __init__(self,
                 mat_deal_id: int = 0,
                 order_code: str = None,
                 status: MaterialDealStatus = None,
                 mat_txn_id: int = 0,
                 material_name: str = 0,
                 quantity: int = 0,
                 offered_cost: int = 0,
                 closed_at: str = None,
                 order_created_at: str = None,
                 description: str = None):
        self.mat_deal_id = mat_deal_id
        self.order_code: str = OrderCode(order_code).sync_cast()
        self.status = status
        self.mat_txn_id = mat_txn_id
        self.material_name = material_name
        self.quantity = quantity
        self.offered_cost = offered_cost
        self.closed_at = funcs.to_utc(closed_at)
        self.order_created_at = funcs.to_utc(order_created_at)
        self.description = description


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
        self.created_date = funcs.to_utc(created_date)

    # +0.2% per day
    def age_multiplier(self) -> float:
        return 1 + self.age() * ARTIFACT_AGE_MULTIPLIER

    # неповні дні
    def age(self) -> int:
        return 1 + (datetime.now(timezone.utc) - self.created_date).days

    def get_owner_profit(self) -> int:
        return round(ARTIFACT_OWNER_PROFIT_RATE * self.investment)
