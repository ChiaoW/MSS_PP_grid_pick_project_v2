from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.core.database import Base

class AllocationLog(Base):
    __tablename__ = "allocation_logs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    grid_id = Column(String(50), nullable=False, index=True)
    route = Column(String(50), nullable=False)
    borrower = Column(String(100), nullable=False)
    grid_type = Column(String(50), nullable=True) # 保留給演算法學習使用
    created_at = Column(DateTime(timezone=True), server_default=func.now())