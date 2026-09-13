from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.security import create_access_token
from app.schemas.user import UserCreate, UserOut, Token
from app.services import crud

from app.models.user import User
from app.api.deps import get_current_user
from app.schemas.expense import ExpenseCreate, ExpenseOut, ExpenseDecision
from app.worker.tasks import analyze_expense_task

from fastapi import WebSocket, WebSocketDisconnect
from app.services.ws_manager import manager


router = APIRouter(prefix="/users", tags=["Users"])
auth_router = APIRouter(prefix="/auth", tags=["Auth"])

expense_router = APIRouter(prefix="/expenses", tags=["Expenses"])


@router.post("/", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register_user(user_in: UserCreate, db: Session = Depends(get_db)):
    user = crud.get_user_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="Користувач із таким email вже існує."
        )
    return crud.create_user(db=db, user_in=user_in)


@auth_router.post("/login", response_model=Token)
def login_for_access_token(
        db: Session = Depends(get_db),
        form_data: OAuth2PasswordRequestForm = Depends()
):
    user = crud.authenticate_user(db, email=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Невірний email або пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(subject=user.email)
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserOut)
def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user


@expense_router.get("/", response_model=List[ExpenseOut])
def read_my_expenses(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return crud.get_my_expenses(db=db, employee_id=current_user.id)


@expense_router.post("/", response_model=ExpenseOut, status_code=status.HTTP_201_CREATED)
def create_new_expense(
        expense_in: ExpenseCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    new_expense = crud.create_expense(db=db, expense_in=expense_in, employee_id=current_user.id)

    if not new_expense:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Вказана категорія не знайдена"
        )

    analyze_expense_task.delay(
        expense_id=new_expense.id,
        description=new_expense.description,
        amount=float(new_expense.amount)
    )

    return new_expense


@expense_router.get("/approvals", response_model=List[ExpenseOut])
def read_expenses_for_approval(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    if not current_user.is_approver:
        raise HTTPException(status_code=403, detail="Доступ заборонено")
    return crud.get_expenses_for_approval(db=db, approver_id=current_user.id)


@expense_router.patch("/{expense_id}/review", response_model=ExpenseOut)
async def review_expense_endpoint(
        expense_id: int,
        decision_in: ExpenseDecision,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    if not current_user.is_approver:
        raise HTTPException(status_code=403, detail="Доступ заборонено")

    if decision_in.decision == "reject" and not decision_in.comment:
        raise HTTPException(
            status_code=400,
            detail="Коментар обов'язковий при відхиленні заявки"
        )

    updated_expense = crud.review_expense(
        db=db,
        expense_id=expense_id,
        approver_id=current_user.id,
        decision=decision_in.decision,
        comment=decision_in.comment
    )

    if not updated_expense:
        raise HTTPException(status_code=404, detail="Заявка не знайдена або ти не є її модератором")


    await manager.send_personal_message(
        {
            "event": "status_update",
            "expense_id": updated_expense.id,
            "new_status": updated_expense.status,
            "decision_comment": updated_expense.rejection_comment
        },
        user_id=updated_expense.employee_id
    )

    return updated_expense


@expense_router.patch("/{expense_id}/withdraw", response_model=ExpenseOut)
def withdraw_expense_endpoint(
    expense_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    updated_expense = crud.withdraw_expense(db=db, expense_id=expense_id, employee_id=current_user.id)
    if not updated_expense:
        raise HTTPException(
            status_code=400,
            detail="Заявка не знайдена або вже оброблена (можна відкликати лише pending)"
        )
    return updated_expense


@expense_router.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int):
    await manager.connect(websocket, user_id)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)