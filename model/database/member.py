from sqlalchemy import Column, Integer, Text, text, Float
from sqlalchemy.orm import relationship

from .base import Base


class Member(Base):
    __tablename__ = 'members'

    user_id = Column(Integer, primary_key=True)
    username = Column(Text)
    first_name = Column(Text)
    last_name = Column(Text)
    tickets = Column(Float, nullable=False, server_default=text('0'))
    tpay_available = Column(Integer, nullable=False, server_default=text('3'))

    artifacts = relationship(
        'Artifact',
        back_populates='owner'
    )
    awards = relationship(
        'AwardMember',
        back_populates='member'
    )
    addt_transactions = relationship(
        'AddtTransaction',
        back_populates='user'
    )
    delt_transactions = relationship(
        'DeltTransaction',
        back_populates='user'
    )
    sent_transactions = relationship(
        'TpayTransaction',
        back_populates='sender',
        foreign_keys='TpayTransaction.sender_id'
    )
    received_transactions = relationship(
        'TpayTransaction',
        back_populates='receiver',
        foreign_keys='TpayTransaction.receiver_id'
    )
    employees_positions = relationship(
        'EmployeeAssignment',
        back_populates='member'
    )
    employment_history = relationship(
        'EmploymentHistory',
        back_populates='member'
    )
