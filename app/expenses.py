from fastapi import APIRouter
from sqlalchemy.orm import Session
from .database import SessionLocal
from .models import Expense
from .schemas import ExpenseCreate, ExpenseResponse


router = APIRouter()


@router.post("/expenses", response_model=ExpenseResponse)
def add_expense(expense: ExpenseCreate):

    db: Session = SessionLocal()

    db_expense = Expense(**expense.model_dump())

    db.add(db_expense)
    db.commit()
    db.refresh(db_expense)

    return db_expense