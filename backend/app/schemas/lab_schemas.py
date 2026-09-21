from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict
from app.models.computer import ComputerStatus

class HardwareSpecs(BaseModel):
    processor: str
    ram_gb: int
    storage: str
    operating_system: str

class MaintenanceLogOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    new_status: ComputerStatus
    previous_status: Optional[ComputerStatus] = None
    action_type: str
    title: str
    description: str
    technician_name: str
    created_at: datetime

class ComputerSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    patrimony: str
    hostname: Optional[str] = None
    ip_address: Optional[str] = None
    mac_address: Optional[str] = None
    status: ComputerStatus
    specs: HardwareSpecs
    notes: Optional[str] = None
    latest_incident: Optional[str] = None
    grid_position: Optional[dict] = None
    history: List[MaintenanceLogOut] = []

class LabKPIs(BaseModel):
    total_machines: int
    operational_count: int
    maintenance_count: int
    damaged_count: int
    obsolete_count: int
    operational_rate: float
    requires_attention: bool

class LabPanoramaResponse(BaseModel):
    lab_id: int
    lab_name: str
    floor: str
    capacity: int
    responsible_person: Optional[str] = None
    kpis: LabKPIs
    computers: List[ComputerSummary]

class LabListItem(BaseModel):
    id: int
    name: str
    capacity: int
    floor: str
    responsible_person: Optional[str] = None
    total_computers: int
    operational_count: int
    maintenance_count: int

class QuickStatusUpdatePayload(BaseModel):
    patrimony: str
    new_status: ComputerStatus
    reason: str = "Ação rápida via Dashboard"
    technician_name: str = "Suporte Senac TI"

class CreateMaintenanceLogPayload(BaseModel):
    patrimony: str
    title: str
    description: str
    action_type: str = "Chamado Técnico"
    technician_name: str = "Suporte Senac TI"
