export type ComputerStatus = 'OPERATIONAL' | 'MAINTENANCE' | 'DAMAGED' | 'OBSOLETE';

export interface HardwareSpecs {
  processor: string;
  ram_gb: number;
  storage: string;
  operating_system: string;
}

export interface MaintenanceLog {
  id: number;
  new_status: ComputerStatus;
  previous_status?: ComputerStatus | null;
  action_type: string;
  title: string;
  description: string;
  technician_name: string;
  created_at: string;
}

export interface ComputerSummary {
  id: number;
  patrimony: string;
  hostname?: string;
  ip_address?: string;
  mac_address?: string;
  status: ComputerStatus;
  specs: HardwareSpecs;
  notes?: string;
  latest_incident?: string;
  grid_position?: {
    row: number;
    col: number;
  };
  history: MaintenanceLog[];
}

export interface LabKPIs {
  total_machines: number;
  operational_count: number;
  maintenance_count: number;
  damaged_count: number;
  obsolete_count: number;
  operational_rate: number;
  requires_attention: boolean;
}

export interface LabPanoramaResponse {
  lab_id: number;
  lab_name: string;
  floor: string;
  capacity: number;
  responsible_person?: string;
  kpis: LabKPIs;
  computers: ComputerSummary[];
}

export interface LabListItem {
  id: number;
  name: string;
  capacity: number;
  floor: string;
  responsible_person?: string;
  total_computers: number;
  operational_count: number;
  maintenance_count: number;
}
