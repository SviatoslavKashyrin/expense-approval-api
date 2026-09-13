from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.category import Category
from app.models.expense import Expense
from app.schemas.user import UserCreate
from app.schemas.expense import ExpenseCreate
from app.core.security import hash_password, verify_password


def get_user_by_email(db: Session, email: str) -> User | None:
    result = db.execute(select(User).where(User.email == email))
    return result.scalars().first()


def create_user(db: Session, user_in: UserCreate) -> User:
    db_user = User(
        email=user_in.email,
        hashed_password=hash_password(user_in.password),
        full_name=user_in.full_name,
        is_approver=user_in.is_approver
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def authenticate_user(db: Session, email: str, password: str) -> User | None:
    user = get_user_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def create_expense(db: Session, expense_in: ExpenseCreate, employee_id: int) -> Expense | None:
    category = db.execute(select(Category).where(Category.id == expense_in.category_id)).scalars().first()

    if not category:
        return None

    db_expense = Expense(
        amount=expense_in.amount,
        category_id=expense_in.category_id,
        description=expense_in.description,
        expense_date=expense_in.expense_date,
        payment_details=expense_in.payment_details,
        employee_id=employee_id,
        approver_id=category.approver_id
    )

    db.add(db_expense)
    db.commit()
    db.refresh(db_expense)
    return db_expense


def get_my_expenses(db: Session, employee_id: int):
    result = db.execute(select(Expense).where(Expense.employee_id == employee_id))
    return list(result.scalars().all())


def get_expenses_for_approval(db: Session, approver_id: int):
    result = db.execute(select(Expense).where(Expense.approver_id == approver_id))
    return list(result.scalars().all())


def review_expense(db: Session, expense_id: int, approver_id: int, decision: str,
                   comment: str | None) -> Expense | None:
    expense = db.execute(
        select(Expense).where(Expense.id == expense_id, Expense.approver_id == approver_id)
    ).scalars().first()

    if not expense:
        return None

    expense.status = "approved" if decision == "approve" else "rejected"
    expense.rejection_comment = comment
    expense.decided_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(expense)
    return expense


def withdraw_expense(db: Session, expense_id: int, employee_id: int) -> Expense | None:
    expense = db.execute(
        select(Expense).where(Expense.id == expense_id, Expense.employee_id == employee_id)
    ).scalars().first()

    if not expense or expense.status != "pending":
        return None

    expense.status = "withdrawn"
    db.commit()
    db.refresh(expense)
    return expense