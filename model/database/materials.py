from sqlalchemy import Column, Integer, Text, Float, ForeignKey
from sqlalchemy.orm import relationship

from .base import Base


class Material(Base):
    __tablename__ = 'materials'

    id = Column(Integer, primary_key=True, autoincrement=True)
    emoji = Column(Text)
    name = Column(Text, nullable=False)
    type_ = Column('type_', Text)
    price = Column(Float, nullable=False, server_default='0')
    description = Column(Text)


class CraftRecipe(Base):
    __tablename__ = 'craft_recipes'

    id = Column(Integer, primary_key=True, autoincrement=True)
    result_id = Column(Integer, ForeignKey('materials.id'), nullable=False)

    result = relationship(
        'Material',
        foreign_keys=[result_id]
    )
    ingredients = relationship(
        'Material',
        secondary='recipe_ingredients',
        backref='used_in_recipes'
    )


class RecipeIngredient(Base):
    __tablename__ = 'recipe_ingredients'

    recipe_id = Column(Integer, ForeignKey('craft_recipes.id'), primary_key=True)
    material_id = Column(Integer, ForeignKey('materials.id'), primary_key=True)
