from sqlalchemy import Column, Integer, ForeignKey, Text
from sqlalchemy.orm import relationship

from .base import Base


class Artifact(Base):
    __tablename__ = 'artifacts'

    artifact_id = Column(Integer, primary_key=True, autoincrement=True)
    owner_id = Column(Integer, ForeignKey('members.user_id'))
    name = Column(Text, nullable=False)
    description = Column(Text)

    owner = relationship(
        'Member',
        back_populates='artifacts'
    )
