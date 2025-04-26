from sqlalchemy import Column, Integer, Text, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from .base import Base


class Award(Base):
    __tablename__ = 'awards'

    award_id = Column(Text, primary_key=True)
    name = Column(Text, unique=True, nullable=False)
    description = Column(Text, nullable=False)
    payment = Column(Float, nullable=False)

    award_members = relationship(
        'AwardMember',
        back_populates='award'
    )


class AwardMember(Base):
    __tablename__ = 'award_member'

    award_id = Column(Text, ForeignKey('awards.award_id', ondelete='CASCADE'), primary_key=True)
    owner_id = Column(Integer, ForeignKey('members.user_id', ondelete='CASCADE'), primary_key=True)
    issue_date = Column(DateTime, nullable=False)

    award = relationship(
        'Award',
        back_populates='award_members'
    )
    member = relationship(
        'Member',
        back_populates='awards'
    )
