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
    decision: str
    comment: Optional[str] = None


class ExpenseOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    amount: Decimal
    category_id: int
    description: str
    expense_date: date
    payment_details: str
    status: str
    rejection_comment: Optional[str] = None
    created_at: datetime
    decided_at: Optional[datetime] = None

    ai_status: str | None = None
    ai_flag: bool | None = None
    ai_flag_reason: str | None = None
    ai_summary: str | None = None


class ExpenseApproverOut(ExpenseOut):
    employee_id: int
    employee_name: str
    employee_email: str