import logging
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.computer import Laboratory, Computer, MaintenanceLog, ComputerStatus

logger = logging.getLogger("seed")

LAB_REAL_DATA = {
    1: {
        "name": "Laboratório 1",
        "description": "Laboratório de Informática Básica e Programação Web",
        "floor": "1º Pavimento - Bloco A",
        "responsible": "Prof. João",
        "capacity": 28,
        "patrimonies": [
            '024008', '023402', '024398', '024019', '024020', '023999', '023972', '023968',
            '024419', '023977', '024021', '024007', '024392', '023994', '024005', '024027',
            '024006', '024001', '024022', '023997', '024010', '023966', '024024', '024002',
            '024000', '023987', '024029', '023975'
        ],
        "default_specs": {
            "processor": "Intel Core i5-10400 (6C/12T 2.9GHz)",
            "ram_gb": 16,
            "storage": "SSD 256GB NVMe",
            "operating_system": "Windows 11 Pro Edu"
        },
        "custom_statuses": {
            "024029": {
                "status": ComputerStatus.MAINTENANCE,
                "note": "Lentidão extrema (Processador obsoleto)",
                "processor": "Intel Core i3-4150 (3.5GHz)",
                "ram_gb": 8,
                "storage": "HD 500GB SATA",
                "operating_system": "Windows 10 Pro"
            },
            "024398": {
                "status": ComputerStatus.DAMAGED,
                "note": "Fonte ATX queimada após sobretensão na rede",
            },
            "023999": {
                "status": ComputerStatus.OBSOLETE,
                "note": "Equipamento antigo marcado para doação/descarte",
                "processor": "Intel Core 2 Duo E7500",
                "ram_gb": 4,
                "storage": "HD 160GB",
                "operating_system": "Windows 7 Pro"
            }
        }
    },
    2: {
        "name": "Laboratório 2",
        "description": "Laboratório de Redes, Infraestrutura e Sistemas Operacionais",
        "floor": "1º Pavimento - Bloco A",
        "responsible": "Coord. Técnica",
        "capacity": 28,
        "patrimonies": [
            '024016', '023996', '023989', '024009', '024023', '023983', '023992', '023991',
            '023974', '023990', '023985', '023979', '024014', '024013', '023981', '023973',
            '023998', '024003', '024028', '023963', '024025', '023982', '024026', '023978',
            '023976', '023980', '024012', '024015'
        ],
        "default_specs": {
            "processor": "Intel Core i5-11400 (6C/12T 2.6GHz)",
            "ram_gb": 16,
            "storage": "SSD 512GB NVMe",
            "operating_system": "Windows 11 Pro / Debian 12"
        },
        "custom_statuses": {
            "024009": {
                "status": ComputerStatus.MAINTENANCE,
                "note": "Aguardando substituição de pente de memória RAM"
            }
        }
    },
    3: {
        "name": "Laboratório 3",
        "description": "Laboratório Avançado de Design Gráfico, Multimídia e Banco de Dados",
        "floor": "2º Pavimento - Bloco B",
        "responsible": "Prof. José Chaves",
        "capacity": 30,
        "patrimonies": [
            '033216', '033217', '033218', '033219', '033220', '033221', '033222', '033223',
            '033224', '033225', '033226', '033227', '033233', '033232', '033231', '033230',
            '033229', '033228', '033245', '033244', '033243', '033242', '033241', '033240',
            '033239', '033238', '033237', '033236', '033235', '033234'
        ],
        "default_specs": {
            "processor": "Intel Core i7-12700 (12C/20T 2.1GHz)",
            "ram_gb": 32,
            "storage": "SSD 1TB NVMe M.2",
            "operating_system": "Windows 11 Pro Edu (Adobe CC Suite)"
        },
        "custom_statuses": {
            "033225": {
                "status": ComputerStatus.MAINTENANCE,
                "note": "Reinstalação do pacote de softwares gráficos"
            }
        }
    }
}

async def seed_initial_data(db: AsyncSession):
    """
    Popula o banco de dados com os laboratórios e computadores reais do Senac Ceilândia.
    Execução segura e idempotente (não duplica se já existirem).
    """
    # Verifica se já existem laboratórios cadastrados
    existing = await db.execute(select(Laboratory))
    if existing.scalars().first():
        logger.info("Banco de dados já contém registros. Ignorando seed.")
        return

    logger.info("Iniciando seed dos Laboratórios do Senac Ceilândia...")

    for lab_key, data in LAB_REAL_DATA.items():
        lab = Laboratory(
            name=data["name"],
            description=data["description"],
            floor=data["floor"],
            capacity=data["capacity"],
            responsible_person=data["responsible"]
        )
        db.add(lab)
        await db.flush()  # Obtém lab.id

        # Cria os computadores
        for idx, pat in enumerate(data["patrimonies"], start=1):
            custom = data.get("custom_statuses", {}).get(pat, {})
            status = custom.get("status", ComputerStatus.OPERATIONAL)
            note = custom.get("note")

            comp = Computer(
                patrimony=pat,
                hostname=f"LAB{lab_key}-PC{idx:02d}",
                ip_address=f"10.20.{lab_key}.{100 + idx}",
                mac_address=f"00:1A:2B:3C:{lab_key:02X}:{idx:02X}",
                status=status,
                processor=custom.get("processor", data["default_specs"]["processor"]),
                ram_gb=custom.get("ram_gb", data["default_specs"]["ram_gb"]),
                storage=custom.get("storage", data["default_specs"]["storage"]),
                operating_system=custom.get("operating_system", data["default_specs"]["operating_system"]),
                notes=note,
                grid_row=(idx - 1) // 6 + 1,
                grid_col=(idx - 1) % 6 + 1,
                laboratory_id=lab.id
            )
            db.add(comp)
            await db.flush()

            # Cria log inicial de manutenção se houver defeito/manutenção
            if status != ComputerStatus.OPERATIONAL:
                log = MaintenanceLog(
                    computer_id=comp.id,
                    previous_status=ComputerStatus.OPERATIONAL,
                    new_status=status,
                    action_type="Triagem Inicial Senac",
                    title=f"Incidente registrado: {note}",
                    description=f"Equipamento classificado como {status.value}. Detalhe: {note}",
                    technician_name="Suporte Técnico Senac"
                )
                db.add(log)

    await db.commit()
    logger.info("Seed concluído com sucesso: 3 Laboratórios e 86 Máquinas cadastradas!")
