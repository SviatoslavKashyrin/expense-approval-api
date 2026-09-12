from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    approver_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    approver = relationship("User", foreign_keys=[approver_id])