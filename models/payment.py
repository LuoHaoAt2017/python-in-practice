from sqlalchemy import Integer, Numeric, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime

from .base import Base, TimestampMixin


class Payment(Base, TimestampMixin):
    """Payment model representing customer payments."""
    __tablename__ = "payment"

    payment_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    customer_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("customer.customer_id"), nullable=False
    )
    staff_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("staff.staff_id"), nullable=False
    )
    rental_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("rental.rental_id"), nullable=False
    )
    amount: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    payment_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    # Relationships
    customer: Mapped["Customer"] = relationship("Customer", back_populates="payments")
    staff: Mapped["Staff"] = relationship("Staff", back_populates="payments")
    rental: Mapped["Rental"] = relationship("Rental", back_populates="payment")

    def __repr__(self):
        return f"<Payment(payment_id={self.payment_id}, amount={self.amount})>"