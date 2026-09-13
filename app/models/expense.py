import enum
from datetime import date, datetime, timezone
from decimal import Decimal

from sqlalchemy import String, ForeignKey, DateTime, Enum, Numeric, Date, Boolean, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class ClaimStatus(str, enum.Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"
    withdrawn = "withdrawn"


class Expense(Base):
    __tablename__ = "expenses"

    id: Mapped[int] = mapped_column(primary_key=True)
    employee_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    approver_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"), nullable=False)

    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    description: Mapped[str] = mapped_column(String(2000), nullable=False)
    payment_details: Mapped[str] = mapped_column(String(1000), nullable=False)
    expense_date: Mapped[date] = mapped_column(Date, nullable=False)

    status: Mapped[ClaimStatus] = mapped_column(Enum(ClaimStatus), default=ClaimStatus.pending, nullable=False)
    rejection_comment: Mapped[str | None] = mapped_column(Text, nullable=True)


    ai_status: Mapped[str] = mapped_column(String(50), default="pending", nullable=False)
    ai_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    ai_flag: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    ai_flag_reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    decided_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    employee = relationship("User", foreign_keys=[employee_id], back_populates="expenses_submitted")
    approver = relationship("User", foreign_keys=[approver_id], back_populates="expenses_to_approve")
    category = relationship("Category")