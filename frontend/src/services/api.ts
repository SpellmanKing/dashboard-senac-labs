import type { LabPanoramaResponse, LabListItem, ComputerStatus } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000/api/v1';

export async function fetchLabPanorama(labId: number): Promise<LabPanoramaResponse> {
  const response = await fetch(`${API_BASE_URL}/labs/${labId}/panorama`);
  if (!response.ok) {
    throw new Error(`Erro ao carregar laboratório ${labId}: ${response.statusText}`);
  }
  return response.json();
}

export async function fetchLabsList(): Promise<LabListItem[]> {
  const response = await fetch(`${API_BASE_URL}/labs`);
  if (!response.ok) {
    throw new Error(`Erro ao carregar lista de laboratórios: ${response.statusText}`);
  }
  return response.json();
}

export async function quickUpdateStatus(
  patrimony: string,
  newStatus: ComputerStatus,
  reason: string,
  technicianName = 'Suporte Senac TI'
): Promise<any> {
  const response = await fetch(`${API_BASE_URL}/labs/computers/quick-status`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      patrimony,
      new_status: newStatus,
      reason,
      technician_name: technicianName,
    }),
  });

  if (!response.ok) {
    throw new Error(`Erro ao atualizar status: ${response.statusText}`);
  }
  return response.json();
}

export async function addMaintenanceLog(
  patrimony: string,
  title: string,
  description: string,
  technicianName = 'Suporte Senac TI'
): Promise<any> {
  const response = await fetch(`${API_BASE_URL}/labs/computers/maintenance-log`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      patrimony,
      title,
      description,
      action_type: 'Chamado Técnico',
      technician_name: technicianName,
    }),
  });

  if (!response.ok) {
    throw new Error(`Erro ao registrar chamado: ${response.statusText}`);
  }
  return response.json();
}
