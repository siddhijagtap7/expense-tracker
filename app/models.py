from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    username = Column(String, unique=True)


class Expense(Base):

    __tablename__ = "expenses"
    id = Column(Integer, primary_key=True, index=True)
    user_id_paid_by = Column(Integer, ForeignKey("users.id"))
    user_id_expense_for_whom = Column(Integer, ForeignKey("users.id"))
    subcategory = Column(String)
    amount = Column(Float)
    payment_mode = Column(String)
    expense_type = Column(String)
    expense_scope = Column(String)
    description = Column(String)
    expense_date = Column(Date)
    user = relationship("User", foreign_keys=[user_id_paid_by])
    expense_for_user = relationship("User", foreign_keys=[user_id_expense_for_whom])
    category = Column(String)