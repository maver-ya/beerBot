from sqlalchemy import (
    DateTime,
    ForeignKey,
    Numeric,
    String,
    func
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime

from ..base import Base


class DrinkEvent(Base):
    __tablename__ = "drink_events"

    id: Mapped[int] = mapped_column(primary_key=True)

    chat_id: Mapped[int] = mapped_column(
        ForeignKey("chats.id", ondelete="CASCADE")
    )
    creator_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE")
    )

    beer_name: Mapped[str] = mapped_column(String(100))
    volume_l: Mapped[float] = mapped_column(Numeric(4, 2))  # литры
    price_rub: Mapped[float] = mapped_column(Numeric(8, 2))

    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now()
    )

    # Связь с участниками
    participants: Mapped[list["DrinkParticipant"]] = relationship(
        "DrinkParticipant",
        back_populates="event",
        cascade="all, delete"
    )


class DrinkParticipant(Base):
    __tablename__ = "drink_participants"

    id: Mapped[int] = mapped_column(primary_key=True)

    drink_event_id: Mapped[int] = mapped_column(
        ForeignKey("drink_events.id", ondelete="CASCADE")
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE")
    )

    share: Mapped[float] = mapped_column(Numeric(3, 2))  # 1.0, 0.5 и т.д.

    # Связь обратно на событие
    event: Mapped["DrinkEvent"] = relationship(
        "DrinkEvent", back_populates="participants"
    )


from sqlalchemy import Column, Integer, BigInteger, DateTime
from datetime import datetime


class Drink(Base):
    __tablename__ = "drinks"

    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, nullable=False)
    amount = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
