from sqlalchemy import Column, Integer, Text, text, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from .base import Base


class SalaryPayout(Base):
    __tablename__ = 'salary_payouts'

    salary_payout_id = Column(Integer, primary_key=True, autoincrement=True)
    plan_date = Column(DateTime, nullable=False)
    fact_date = Column(DateTime)
    paid_out = Column(Integer, nullable=False, server_default=text('0'))


class PositionCatalogueRecord(Base):
    __tablename__ = 'position_catalogue'

    position = Column(Text, primary_key=True)
    name_uk = Column(Text, nullable=False)
    salary = Column(Float, nullable=False, server_default=text('0'))

    employees_positions = relationship(
        'EmployeeAssignment',
        back_populates='position_catalogue'
    )
    employment_history = relationship(
        'EmploymentHistory',
        back_populates='position_catalogue'
    )


class EmployeeAssignment(Base):
    __tablename__ = 'employees'

    user_id = Column(Integer, ForeignKey('members.user_id', ondelete='RESTRICT'), primary_key=True)
    position = Column(Text, ForeignKey('position_catalogue.position', ondelete='RESTRICT'), primary_key=True)
    hired_date = Column(DateTime, nullable=False)

    member = relationship(
        'Member',
        back_populates='employees_positions'
    )
    position_catalogue = relationship(
        'PositionCatalogueRecord',
        back_populates='employees_positions'
    )


class EmploymentHistory(Base):
    __tablename__ = 'employment_history'

    employment_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('members.user_id', ondelete='RESTRICT'), nullable=False)
    position = Column(Text, ForeignKey('position_catalogue.position', ondelete='RESTRICT'), nullable=False)
    hired_date = Column(DateTime, nullable=False)
    fired_date = Column(DateTime, nullable=False)

    member = relationship(
        'Member',
        back_populates='employment_history'
    )
    position_catalogue = relationship(
        'PositionCatalogueRecord',
        back_populates='employment_history'
    )
