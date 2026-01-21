from sqlalchemy import Column, Integer, String, BigInteger
from ..base import Base

class Achievement(Base):
    __tablename__ = "achievements"

    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, nullable=False)
    level = Column(Integer, nullable=False)  # 1, 5, 10, 25, 50 литров
    description = Column(String, nullable=False)
