from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.models.computer import Laboratory, Computer, ComputerStatus, MaintenanceLog
from app.schemas.lab_schemas import (
    LabPanoramaResponse,
    LabListItem,
    LabKPIs,
    ComputerSummary,
    HardwareSpecs,
    MaintenanceLogOut,
    QuickStatusUpdatePayload,
    CreateMaintenanceLogPayload
)

router = APIRouter(prefix="/labs", tags=["Laboratórios e Ativos"])

@router.get("", response_model=List[LabListItem])
async def list_laboratories(db: AsyncSession = Depends(get_db)):
    """
    Retorna a lista de todos os laboratórios com contadores de máquinas.
    """
    stmt = (
        select(Laboratory)
        .options(selectinload(Laboratory.computers))
        .where(Laboratory.is_active == True)
        .order_by(Laboratory.id)
    )
    result = await db.execute(stmt)
    labs = result.scalars().all()

    items = []
    for lab in labs:
        total = len(lab.computers)
        op = sum(1 for c in lab.computers if c.status == ComputerStatus.OPERATIONAL)
        maint = sum(1 for c in lab.computers if c.status == ComputerStatus.MAINTENANCE)
        items.append(
            LabListItem(
                id=lab.id,
                name=lab.name,
                capacity=lab.capacity,
                floor=lab.floor,
                responsible_person=lab.responsible_person,
                total_computers=total,
                operational_count=op,
                maintenance_count=maint
            )
        )
    return items

@router.get("/{lab_id}/panorama", response_model=LabPanoramaResponse)
async def get_lab_panorama(
    lab_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Retorna o panorama completo de um laboratório específico:
    - KPIs em tempo real (Total, Bom Estado, Manutenção, Danificado, Obsoleto, % Operacional)
    - Lista de computadores com especificações de hardware, IP e incidentes
    """
    query = (
        select(Laboratory)
        .options(
            selectinload(Laboratory.computers).selectinload(Computer.maintenance_logs)
        )
        .where(Laboratory.id == lab_id)
    )
    result = await db.execute(query)
    lab = result.scalar_one_or_none()

    if not lab:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Laboratório ID {lab_id} não encontrado."
        )

    # Cálculo dos KPIs
    total = len(lab.computers)
    op_count = sum(1 for c in lab.computers if c.status == ComputerStatus.OPERATIONAL)
    maint_count = sum(1 for c in lab.computers if c.status == ComputerStatus.MAINTENANCE)
    damaged_count = sum(1 for c in lab.computers if c.status == ComputerStatus.DAMAGED)
    obsolete_count = sum(1 for c in lab.computers if c.status == ComputerStatus.OBSOLETE)
    
    op_rate = round((op_count / total * 100), 1) if total > 0 else 0.0

    kpis = LabKPIs(
        total_machines=total,
        operational_count=op_count,
        maintenance_count=maint_count,
        damaged_count=damaged_count,
        obsolete_count=obsolete_count,
        operational_rate=op_rate,
        requires_attention=(maint_count + damaged_count) > 2
    )

    # Formatação dos computadores
    computer_summaries = []
    for comp in lab.computers:
        logs_out = [
            MaintenanceLogOut.model_validate(log) for log in comp.maintenance_logs[:5]
        ]
        latest_incident = comp.notes
        if not latest_incident and comp.maintenance_logs:
            latest_incident = comp.maintenance_logs[0].description

        computer_summaries.append(
            ComputerSummary(
                id=comp.id,
                patrimony=comp.patrimony,
                hostname=comp.hostname,
                ip_address=comp.ip_address,
                mac_address=comp.mac_address,
                status=comp.status,
                specs=HardwareSpecs(
                    processor=comp.processor,
                    ram_gb=comp.ram_gb,
                    storage=comp.storage,
                    operating_system=comp.operating_system
                ),
                notes=comp.notes,
                latest_incident=latest_incident,
                grid_position={"row": comp.grid_row, "col": comp.grid_col} if comp.grid_row else None,
                history=logs_out
            )
        )

    return LabPanoramaResponse(
        lab_id=lab.id,
        lab_name=lab.name,
        floor=lab.floor,
        capacity=lab.capacity,
        responsible_person=lab.responsible_person,
        kpis=kpis,
        computers=computer_summaries
    )

@router.get("/computers/{patrimony}", response_model=ComputerSummary)
async def get_computer_by_patrimony(
    patrimony: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Retorna os detalhes completos de um computador específico pelo número de patrimônio.
    """
    stmt = (
        select(Computer)
        .options(selectinload(Computer.maintenance_logs))
        .where(Computer.patrimony == patrimony)
    )
    res = await db.execute(stmt)
    comp = res.scalar_one_or_none()

    if not comp:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patrimônio {patrimony} não encontrado."
        )

    logs_out = [MaintenanceLogOut.model_validate(l) for l in comp.maintenance_logs]

    return ComputerSummary(
        id=comp.id,
        patrimony=comp.patrimony,
        hostname=comp.hostname,
        ip_address=comp.ip_address,
        mac_address=comp.mac_address,
        status=comp.status,
        specs=HardwareSpecs(
            processor=comp.processor,
            ram_gb=comp.ram_gb,
            storage=comp.storage,
            operating_system=comp.operating_system
        ),
        notes=comp.notes,
        latest_incident=comp.notes,
        grid_position={"row": comp.grid_row, "col": comp.grid_col} if comp.grid_row else None,
        history=logs_out
    )

@router.post("/computers/quick-status", status_code=status.HTTP_200_OK)
async def quick_update_computer_status(
    payload: QuickStatusUpdatePayload,
    db: AsyncSession = Depends(get_db)
):
    """
    Atualiza o status de uma máquina em 1 clique e cria o log de manutenção correspondente.
    """
    stmt = select(Computer).where(Computer.patrimony == payload.patrimony)
    result = await db.execute(stmt)
    computer = result.scalar_one_or_none()

    if not computer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Máquina com patrimônio {payload.patrimony} não encontrada."
        )

    old_status = computer.status
    computer.status = payload.new_status
    computer.notes = payload.reason if payload.new_status != ComputerStatus.OPERATIONAL else None

    # Registra no log de manutenção
    log = MaintenanceLog(
        computer_id=computer.id,
        previous_status=old_status,
        new_status=payload.new_status,
        action_type="Ação Rápida no Dashboard",
        title=f"Transição: {old_status.value} ➔ {payload.new_status.value}",
        description=payload.reason,
        technician_name=payload.technician_name
    )
    db.add(log)
    await db.commit()

    return {
        "success": True,
        "message": f"Patrimônio #{payload.patrimony} atualizado com sucesso.",
        "patrimony": payload.patrimony,
        "new_status": payload.new_status
    }

@router.post("/computers/maintenance-log", status_code=status.HTTP_201_CREATED)
async def create_maintenance_log(
    payload: CreateMaintenanceLogPayload,
    db: AsyncSession = Depends(get_db)
):
    """
    Adiciona um chamado de suporte ou nota técnica manual a uma máquina.
    """
    stmt = select(Computer).where(Computer.patrimony == payload.patrimony)
    result = await db.execute(stmt)
    computer = result.scalar_one_or_none()

    if not computer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Máquina com patrimônio {payload.patrimony} não encontrada."
        )

    log = MaintenanceLog(
        computer_id=computer.id,
        previous_status=computer.status,
        new_status=computer.status,
        action_type=payload.action_type,
        title=payload.title,
        description=payload.description,
        technician_name=payload.technician_name
    )
    db.add(log)
    await db.commit()

    return {"success": True, "message": "Registro de manutenção criado com sucesso."}
