from pydantic import BaseModel
from datetime import date
from .enums import ExpenseScope, ExpenseType, PaymentMode


class ExpenseCreate(BaseModel):
    user_id_paid_by: int
    user_id_expense_for_whom:int
    category: str
    subcategory: str
    amount: float
    payment_mode: PaymentMode
    expense_type: ExpenseType
    expense_scope: ExpenseScope
    description: str | None = None
    expense_date: date


class ExpenseResponse(BaseModel):
    id: int
    user_id_paid_by: int
    user_id_expense_for_whom:int
    category: str
    subcategory: str
    amount: float
    payment_mode: PaymentMode
    expense_type: ExpenseType
    expense_scope: ExpenseScope
    description: str | None
    expense_date: date
    class Config:
        from_attributes = True