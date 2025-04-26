from sqlalchemy import Column, Integer, Float, DateTime

from .base import Base


class PriceReset(Base):
    __tablename__ = 'price_history'

    price_history_id = Column(Integer, primary_key=True, autoincrement=True)
    inflation = Column(Float, nullable=False)
    fluctuation = Column(Float, nullable=False)
    plan_date = Column(DateTime, nullable=False)
    fact_date = Column(DateTime, nullable=False)
