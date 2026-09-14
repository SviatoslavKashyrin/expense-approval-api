from app.worker.celery_app import celery_app
from app.services.ai_service import analyze_expense_data
from app.models.expense import Expense
from app.api.deps import SessionLocal


@celery_app.task(name="analyze_expense")
def analyze_expense_task(expense_id: int, description: str, amount: float):
    db = SessionLocal()
    try:
        ai_result = analyze_expense_data(description, amount)

        expense = db.query(Expense).filter(Expense.id == expense_id).first()
        if expense:
            expense.ai_status = ai_result["ai_status"]
            expense.ai_flag = ai_result["ai_flag"]
            expense.ai_flag_reason = ai_result["ai_flag_reason"]
            expense.ai_summary = ai_result["ai_summary"]
            db.commit()
    finally:
        db.close()