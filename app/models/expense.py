import enum
from datetime import datetime, timezone

from sqlalchemy import String, Float, ForeignKey, DateTime, Enum
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

    amount: Mapped[float] = mapped_column(Float, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False)
    payment_details: Mapped[str] = mapped_column(String, nullable=False)

    status: Mapped[ClaimStatus] = mapped_column(Enum(ClaimStatus), default=ClaimStatus.pending, nullable=False)
    approver_comment: Mapped[str] = mapped_column(String, nullable=True)
    ai_summary: Mapped[str] = mapped_column(String, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    employee = relationship("User", foreign_keys=[employee_id], back_populates="expenses_submitted")
    approver = relationship("User", foreign_keys=[approver_id], back_populates="expenses_to_approve")
    category = relationship("Category")