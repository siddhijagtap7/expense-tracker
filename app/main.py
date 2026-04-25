from fastapi import FastAPI, Query, Request
from fastapi.responses import StreamingResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from datetime import datetime 
import pandas as pd
import io
from sqlalchemy.orm import Session
from .expenses import router as expense_router
from .database import engine, SessionLocal
from .models import Base, Expense, User
from .analytics import (
    category_spending,
    paid_for_spending,
    user_family_spending,
    needed_vs_unneeded,
    monthly_spending
)
from sqlalchemy import func
from app.config.config import CATEGORY_MAPPING

Base.metadata.create_all(bind=engine)

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/")
def home(request: Request, month: str = "all"):
    db = SessionLocal()
    try:
        query = db.query(Expense)
        
        if month != "all":
            target_month = month.zfill(2)
            query = query.filter(func.strftime('%m', Expense.expense_date) == target_month)
        
        expenses = query.order_by(Expense.expense_date.desc()).all()
        
        return templates.TemplateResponse(
            "dashboard.html", 
            {"request": request, "expenses": expenses, "current_month": month}
        )
    finally:
        db.close()

app.include_router(expense_router)

@app.get("/users")
def get_users():

    db = SessionLocal()

    users = db.query(User).all()

    return users

@app.get("/add-expense")
def add_expense_page(request: Request):

    return templates.TemplateResponse(
        "add_expense.html",
        {"request": request}
    )

@app.get("/analytics-data")
def analytics_data(month: str = "all"):
    db = SessionLocal()
    try:
        # Convert "all" to None, otherwise cast to int
        m = int(month) if month != "all" else None

        return {
            "category": category_spending(db, m),
            "family_contribution": user_family_spending(db, m),
            "paid_for": paid_for_spending(db, m),
            "needed_unneeded": needed_vs_unneeded(db, m),
            "monthly": monthly_spending(db),
        }
    finally:
        db.close()

@app.get("/analytics")
def analytics_page(request: Request):

    return templates.TemplateResponse(
        "analytics.html",
        {"request": request}
    )
  
@app.delete("/delete-expense/{expense_id}")
async def delete_expense(expense_id: int):
    db = SessionLocal()
    try:
        expense = db.query(Expense).filter(Expense.id == expense_id).first()
        if not expense:
            return {"status": "error", "message": "Expense not found"}, 404
        
        db.delete(expense)
        db.commit()
        return {"status": "success", "message": "Expense deleted"}
    except Exception as e:
        db.rollback()
        return {"status": "error", "message": str(e)}, 500
    finally:
        db.close()
  
@app.get("/categories")
def get_categories():
    sorted_mapping = {
        category: sorted(subcategories)
        for category, subcategories in sorted(CATEGORY_MAPPING.items())
    }

    return sorted_mapping

@app.get("/download-expenses")
def download_expenses(month: str = "all"):
    db = SessionLocal()
    try:
        query = db.query(Expense)
        
        # Apply the same filter logic as the dashboard
        if month != "all":
            target_month = month.zfill(2)
            query = query.filter(func.strftime('%m', Expense.expense_date) == target_month)
        
        expenses = query.order_by(Expense.expense_date.desc()).all()

        # Convert SQLAlchemy objects to a list of dictionaries for Pandas
        data = []
        for e in expenses:
            data.append({
                "Date": e.expense_date,
                "Paid by": e.user.name if e.user else "",
                "Expense for whom": e.expense_for_user.name if e.expense_for_user else "",
                "Category": e.category,
                "Subcategory": e.subcategory,
                "Payment Mode": e.payment_mode,
                "Expense Type": e.expense_type,
                "Expense Scope": e.expense_scope,
                "Description": e.description,
                "Amount": e.amount
            })

        # Create DataFrame and save to Excel in memory (BytesIO)
        df = pd.DataFrame(data)
        output = io.BytesIO()
        
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Expenses')
        
        output.seek(0)

        filename = f"expenses_{month}_{datetime.now().strftime('%Y-%m-%d')}.xlsx"
        headers = {"Content-Disposition": f'attachment; filename="{filename}"'}
        
        return StreamingResponse(
            output, 
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers=headers
        )
    finally:
        db.close()

@app.get("/edit-expense/{expense_id}")
def edit_expense_page(request: Request, expense_id: int):
    db = SessionLocal()
    try:
        expense = db.query(Expense).filter(Expense.id == expense_id).first()
        if not expense:
            return RedirectResponse(url="/", status_code=303)
        return templates.TemplateResponse(
            "edit_expense.html", 
            {"request": request, "expense": expense}
        )
    finally:
        db.close()


@app.post("/update-expense/{expense_id}")
async def update_expense(expense_id: int, request: Request):
    data = await request.json()
    db = SessionLocal()
    try:
        expense = db.query(Expense).filter(Expense.id == expense_id).first()
        if expense:
            date_obj = datetime.strptime(data['expense_date'], '%Y-%m-%d').date()
            expense.user_id_paid_by = int(data['user_id_paid_by'])
            expense.user_id_expense_for_whom = int(data['user_id_expense_for_whom'])
            expense.category = data['category']
            expense.subcategory = data['subcategory']
            expense.amount = float(data['amount'])
            expense.payment_mode = data['payment_mode']
            expense.expense_type = data['expense_type']
            expense.expense_scope = data['expense_scope']
            expense.description = data['description']
            
            # Use the converted date object here
            expense.expense_date = date_obj 
            
            db.commit()
            return {"status": "success"}
        return {"status": "error", "message": "Expense not found"}, 404
    except Exception as e:
        print(f"Error updating: {e}")
        return {"status": "error", "message": str(e)}, 400
    finally:
        db.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)