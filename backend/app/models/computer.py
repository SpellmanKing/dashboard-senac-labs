import enum
from datetime import datetime
from typing import List, Optional
from sqlalchemy import (
    String,
    Integer,
    DateTime,
    ForeignKey,
    Enum as SQLEnum,
    Text,
    Index,
    func
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base

class ComputerStatus(str, enum.Enum):
    OPERATIONAL = "OPERATIONAL"   # 🟢 Bom Estado (Operacional)
    MAINTENANCE = "MAINTENANCE"   # 🟡 Em Manutenção
    DAMAGED = "DAMAGED"           # 🔴 Danificado / Inoperante
    OBSOLETE = "OBSOLETE"         # ⚪ Obsoleto / Para descarte

class Laboratory(Base):
    __tablename__ = "laboratories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    capacity: Mapped[int] = mapped_column(Integer, default=30, nullable=False)
    floor: Mapped[str] = mapped_column(String(50), default="1º Pavimento")
    responsible_person: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relacionamentos
    computers: Mapped[List["Computer"]] = relationship(
        "Computer", back_populates="laboratory", cascade="all, delete-orphan"
    )

class Computer(Base):
    __tablename__ = "computers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    patrimony: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    hostname: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    mac_address: Mapped[Optional[str]] = mapped_column(String(17), nullable=True)
    
    # Status Operacional
    status: Mapped[ComputerStatus] = mapped_column(
        SQLEnum(ComputerStatus), default=ComputerStatus.OPERATIONAL, index=True, nullable=False
    )
    
    # Especificações de Hardware
    processor: Mapped[str] = mapped_column(String(120), default="Intel Core i5")
    ram_gb: Mapped[int] = mapped_column(Integer, default=16)
    storage: Mapped[str] = mapped_column(String(100), default="SSD 256GB NVMe")
    operating_system: Mapped[str] = mapped_column(String(100), default="Windows 11 Pro")
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Disposição física no Laboratório
    grid_row: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    grid_col: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Chave estrangeira
    laboratory_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("laboratories.id", ondelete="CASCADE"), nullable=False, index=True
    )
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relacionamentos
    laboratory: Mapped["Laboratory"] = relationship("Laboratory", back_populates="computers")
    maintenance_logs: Mapped[List["MaintenanceLog"]] = relationship(
        "MaintenanceLog", back_populates="computer", order_by="desc(MaintenanceLog.created_at)", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("idx_lab_status", "laboratory_id", "status"),
    )

class MaintenanceLog(Base):
    __tablename__ = "maintenance_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    computer_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("computers.id", ondelete="CASCADE"), nullable=False, index=True
    )
    
    previous_status: Mapped[Optional[ComputerStatus]] = mapped_column(SQLEnum(ComputerStatus), nullable=True)
    new_status: Mapped[ComputerStatus] = mapped_column(SQLEnum(ComputerStatus), nullable=False)
    
    action_type: Mapped[str] = mapped_column(String(50), default="Troca de Status")
    title: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    technician_name: Mapped[str] = mapped_column(String(100), default="Suporte Senac TI")
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    computer: Mapped["Computer"] = relationship("Computer", back_populates="maintenance_logs")
