from sqlalchemy import Column, Integer, Text, text, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from .base import Base


class AddtTransaction(Base):
    __tablename__ = 'addt'

    addt_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('members.user_id', ondelete='RESTRICT'), nullable=False)
    tickets = Column(Float, nullable=False, server_default=text('0'))
    time = Column(DateTime, nullable=False)
    description = Column(Text)
    type_ = Column('type_', Text, nullable=False, server_default=text('unknown'))

    user = relationship('Member', back_populates='addt_transactions')


class DeltTransaction(Base):
    __tablename__ = 'delt'

    delt_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('members.user_id', ondelete='RESTRICT'), nullable=False)
    tickets = Column(Float, nullable=False, server_default=text('0'))
    time = Column(DateTime, nullable=False)
    description = Column(Text)
    type_ = Column('type_', Text, nullable=False, server_default=text('unknown'))

    user = relationship('Member', back_populates='delt_transactions')


class TpayTransaction(Base):
    __tablename__ = 'tpay'

    tpay_id = Column(Integer, primary_key=True, autoincrement=True)
    sender_id = Column(Integer, ForeignKey('members.user_id', ondelete='RESTRICT'), nullable=False)
    receiver_id = Column(Integer, ForeignKey('members.user_id', ondelete='RESTRICT'), nullable=False)
    transfer = Column(Float, nullable=False)
    fee = Column(Float, nullable=False)
    time = Column(DateTime, nullable=False)
    description = Column(Text)

    sender = relationship('Member', foreign_keys=[sender_id], back_populates='sent_transactions')
    receiver = relationship('Member', foreign_keys=[receiver_id], back_populates='received_transactions')
