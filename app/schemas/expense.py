from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ExpenseCreate(BaseModel):
    amount: Decimal = Field(gt=0, description="Сума у USD")
    category_id: int
    description: str = Field(min_length=1, max_length=2000)
    expense_date: date
    payment_details: str = Field(min_length=1, max_length=1000)

    @field_validator("expense_date")
    @classmethod
    def not_in_future(cls, v: date) -> date:
        if v > date.today():
            raise ValueError("Дата витрати не може бути у майбутньому")
        return v


class ExpenseDecision(BaseModel):
    decision: str = Field(description="'approve' або 'reject'")
    comment: Optional[str] = Field(default=None, max_length=2000)

    @field_validator("decision")
    @classmethod
    def valid_decision(cls, v: str) -> str:
        v = v.lower().strip()
        if v not in ("approve", "reject"):
            raise ValueError("decision має бути 'approve' або 'reject'")
        return v

    @field_validator("comment")
    @classmethod
    def comment_required_for_reject(cls, v, info):
        decision = info.data.get("decision")
        if decision == "reject" and (v is None or not v.strip()):
            raise ValueError("Коментар обов'язковий при відхиленні заявки (reject)")
        return v


class ExpenseOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    amount: Decimal
    category: str
    description: str
    expense_date: date
    payment_details: str
    status: str
    rejection_comment: Optional[str] = None
    created_at: datetime
    decided_at: Optional[datetime] = None


class ExpenseApproverOut(ExpenseOut):
    employee_id: int
    employee_name: str
    employee_email: str
    ai_status: str
    ai_summary: Optional[str] = None
    ai_flag: Optional[bool] = None
    ai_flag_reason: Optional[str] = None