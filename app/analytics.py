from sqlalchemy import func, extract
from .models import Expense, User
from app.config.config import CATEGORY_MAPPING

def category_spending(db, month=None):
    query = db.query(Expense.category, func.sum(Expense.amount))
    if month:
        query = query.filter(extract('month', Expense.expense_date) == month)
    
    results = query.group_by(Expense.category).all()
    
    db_data = {r[0]: float(r[1]) for r in results}
    final = {}
    for category in sorted(CATEGORY_MAPPING.keys()):
        final[category] = db_data.get(category, 0)
    return final


def user_family_spending(db, month=None):
    query = (
        db.query(User.name, func.sum(Expense.amount))
        .join(Expense, Expense.user_id_paid_by == User.id)
    )
    if month:
        query = query.filter(extract('month', Expense.expense_date) == month)
        
    results = query.group_by(User.name).all()
    return {r[0]: float(r[1]) for r in results}


def needed_vs_unneeded(db, month=None):
    query = db.query(Expense.expense_type, func.sum(Expense.amount))
    if month:
        query = query.filter(extract('month', Expense.expense_date) == month)
        
    results = query.group_by(Expense.expense_type).all()
    return {r[0]: float(r[1]) for r in results}


def monthly_spending(db):

    results = (
        db.query(
            func.strftime("%Y-%m", Expense.expense_date),
            func.sum(Expense.amount)
        )
        .group_by(func.strftime("%Y-%m", Expense.expense_date))
        .order_by(func.strftime("%Y-%m", Expense.expense_date))
        .all()
    )
    return {r[0]: float(r[1]) for r in results}