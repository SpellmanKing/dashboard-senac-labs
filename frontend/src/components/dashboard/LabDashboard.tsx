import React, { useState, useEffect, useMemo, useCallback } from 'react';
import {
  Monitor,
  CheckCircle2,
  AlertTriangle,
  XCircle,
  Clock,
  Search,
  SlidersHorizontal,
  Cpu,
  Wifi,
  ShieldAlert,
  Building2,
  RefreshCw,
  X,
  History,
  Moon,
  Sun,
  PlusCircle,
  Send,
  Check
} from 'lucide-react';
import {
  fetchLabPanorama,
  quickUpdateStatus,
  addMaintenanceLog
} from '../../services/api';
import type {
  ComputerSummary,
  ComputerStatus,
  LabPanoramaResponse
} from '../../types';

// Configuração visual do Color Coding para cada status
const STATUS_CONFIG: Record<
  ComputerStatus,
  {
    label: string;
    badgeClass: string;
    borderClass: string;
    dotColor: string;
    bgGlow: string;
    icon: React.ComponentType<{ className?: string }>;
  }
> = {
  OPERATIONAL: {
    label: 'Bom Estado',
    badgeClass: 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border-emerald-500/30',
    borderClass: 'hover:border-emerald-500/60 dark:hover:border-emerald-500/50',
    dotColor: 'bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.5)]',
    bgGlow: 'hover:shadow-emerald-500/5',
    icon: CheckCircle2,
  },
  MAINTENANCE: {
    label: 'Em Manutenção',
    badgeClass: 'bg-amber-500/10 text-amber-600 dark:text-amber-400 border-amber-500/30',
    borderClass: 'hover:border-amber-500/60 dark:hover:border-amber-500/50',
    dotColor: 'bg-amber-500 shadow-[0_0_8px_rgba(245,158,11,0.5)]',
    bgGlow: 'hover:shadow-amber-500/5',
    icon: AlertTriangle,
  },
  DAMAGED: {
    label: 'Danificado',
    badgeClass: 'bg-rose-500/10 text-rose-600 dark:text-rose-400 border-rose-500/30',
    borderClass: 'hover:border-rose-500/60 dark:hover:border-rose-500/50',
    dotColor: 'bg-rose-500 shadow-[0_0_8px_rgba(244,63,94,0.5)]',
    bgGlow: 'hover:shadow-rose-500/5',
    icon: XCircle,
  },
  OBSOLETE: {
    label: 'Obsoleto',
    badgeClass: 'bg-slate-500/10 text-slate-600 dark:text-slate-400 border-slate-500/30',
    borderClass: 'hover:border-slate-500/60 dark:hover:border-slate-500/50',
    dotColor: 'bg-slate-400',
    bgGlow: 'hover:shadow-slate-500/5',
    icon: Clock,
  },
};

export const LabDashboard: React.FC = () => {
  const [currentLabId, setCurrentLabId] = useState<number>(1);
  const [labData, setLabData] = useState<LabPanoramaResponse | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  // Filtros
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [selectedStatusFilter, setSelectedStatusFilter] = useState<string>('ALL');

  // Modal de Detalhes
  const [selectedComputer, setSelectedComputer] = useState<ComputerSummary | null>(null);
  const [isSubmittingAction, setIsSubmittingAction] = useState<boolean>(false);
  const [actionSuccessNotice, setActionSuccessNotice] = useState<string | null>(null);

  // Formulário de novo chamado no modal
  const [ticketTitle, setTicketTitle] = useState<string>('');
  const [ticketDesc, setTicketDesc] = useState<string>('');
  const [showTicketForm, setShowTicketForm] = useState<boolean>(false);

  // Dark Mode
  const [isDarkMode, setIsDarkMode] = useState<boolean>(() => {
    return document.documentElement.classList.contains('dark') ||
      window.matchMedia('(prefers-color-scheme: dark)').matches;
  });

  useEffect(() => {
    if (isDarkMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [isDarkMode]);

  // Carrega panorama da API
  const loadPanorama = useCallback(async (labId: number) => {
    setIsLoading(true);
    setErrorMessage(null);
    try {
      const data = await fetchLabPanorama(labId);
      setLabData(data);
      // Se houver computador selecionado no modal, atualiza ele com os dados mais recentes
      if (selectedComputer) {
        const fresh = data.computers.find((c) => c.patrimony === selectedComputer.patrimony);
        if (fresh) setSelectedComputer(fresh);
      }
    } catch (err: any) {
      console.error(err);
      setErrorMessage(err.message || 'Falha ao conectar com o servidor.');
    } finally {
      setIsLoading(false);
    }
  }, [selectedComputer]);

  useEffect(() => {
    loadPanorama(currentLabId);
  }, [currentLabId]);

  // Lista filtrada de computadores
  const filteredComputers = useMemo(() => {
    if (!labData) return [];
    return labData.computers.filter((comp) => {
      const query = searchTerm.toLowerCase();
      const matchSearch =
        comp.patrimony.toLowerCase().includes(query) ||
        (comp.hostname && comp.hostname.toLowerCase().includes(query)) ||
        (comp.ip_address && comp.ip_address.includes(query));
      const matchStatus =
        selectedStatusFilter === 'ALL' || comp.status === selectedStatusFilter;
      return matchSearch && matchStatus;
    });
  }, [labData, searchTerm, selectedStatusFilter]);

  // Ação Rápida de 1-Clique para Alteração de Status
  const handleQuickStatus = async (newStatus: ComputerStatus, defaultReason: string) => {
    if (!selectedComputer) return;
    setIsSubmittingAction(true);
    try {
      await quickUpdateStatus(selectedComputer.patrimony, newStatus, defaultReason);
      setActionSuccessNotice(`Status do PC #${selectedComputer.patrimony} alterado para ${STATUS_CONFIG[newStatus].label}!`);
      setTimeout(() => setActionSuccessNotice(null), 3500);
      await loadPanorama(currentLabId);
    } catch (err: any) {
      alert(`Erro ao alterar status: ${err.message}`);
    } finally {
      setIsSubmittingAction(false);
    }
  };

  // Envio de chamado técnico no modal
  const handleCreateTicket = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedComputer || !ticketTitle || !ticketDesc) return;
    setIsSubmittingAction(true);
    try {
      await addMaintenanceLog(selectedComputer.patrimony, ticketTitle, ticketDesc);
      setTicketTitle('');
      setTicketDesc('');
      setShowTicketForm(false);
      setActionSuccessNotice('Chamado de suporte registrado no histórico!');
      setTimeout(() => setActionSuccessNotice(null), 3500);
      await loadPanorama(currentLabId);
    } catch (err: any) {
      alert(`Erro ao registrar chamado: ${err.message}`);
    } finally {
      setIsSubmittingAction(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-zinc-950 text-slate-800 dark:text-zinc-100 transition-colors duration-200">
      {/* Top Header / Branding Senac */}
      <header className="sticky top-0 z-30 border-b border-slate-200 dark:border-zinc-800 bg-white/85 dark:bg-zinc-900/85 backdrop-blur-md px-4 sm:px-8 py-3.5 shadow-sm">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-[#004A99] flex items-center justify-center text-white shadow-md shadow-blue-900/20 shrink-0">
              <Monitor className="w-6 h-6" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h1 className="font-extrabold text-xl tracking-tight text-slate-900 dark:text-white">
                  Senac TechLab
                </h1>
                <span className="px-2 py-0.5 text-[11px] font-bold tracking-wide uppercase rounded bg-[#F6821F]/15 text-[#F6821F] border border-[#F6821F]/30">
                  Gestão de Ativos
                </span>
              </div>
              <p className="text-xs text-slate-500 dark:text-zinc-400">
                Inventário e Monitoramento de Laboratórios de Informática • Senac Ceilândia
              </p>
            </div>
          </div>

          <div className="flex items-center gap-3 self-end md:self-auto">
            {/* Abas dos Laboratórios */}
            <div className="flex items-center bg-slate-100 dark:bg-zinc-800/90 p-1 rounded-xl border border-slate-200 dark:border-zinc-700/60">
              {[1, 2, 3].map((num) => (
                <button
                  key={num}
                  onClick={() => setCurrentLabId(num)}
                  className={`flex items-center gap-2 px-3 sm:px-4 py-1.5 rounded-lg text-xs sm:text-sm font-semibold transition-all ${
                    currentLabId === num
                      ? 'bg-white dark:bg-zinc-900 text-[#004A99] dark:text-blue-400 shadow-sm'
                      : 'text-slate-600 dark:text-zinc-400 hover:text-slate-900 dark:hover:text-white'
                  }`}
                >
                  <Building2 className="w-3.5 h-3.5" />
                  Lab {num}
                </button>
              ))}
            </div>

            {/* Botão de Atualizar */}
            <button
              onClick={() => loadPanorama(currentLabId)}
              disabled={isLoading}
              title="Atualizar dados do laboratório"
              className="p-2 rounded-xl border border-slate-200 dark:border-zinc-800 hover:bg-slate-100 dark:hover:bg-zinc-800 text-slate-600 dark:text-zinc-300 transition-colors"
            >
              <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin text-[#004A99]' : ''}`} />
            </button>

            {/* Alternador de Dark Mode */}
            <button
              onClick={() => setIsDarkMode(!isDarkMode)}
              title="Alternar tema claro/escuro"
              className="p-2 rounded-xl border border-slate-200 dark:border-zinc-800 hover:bg-slate-100 dark:hover:bg-zinc-800 text-slate-600 dark:text-zinc-300 transition-colors"
            >
              {isDarkMode ? <Sun className="w-4 h-4 text-amber-400" /> : <Moon className="w-4 h-4 text-slate-600" />}
            </button>
          </div>
        </div>
      </header>

      {/* Conteúdo Principal */}
      <main className="max-w-7xl mx-auto px-4 sm:px-8 py-6 space-y-6">
        {/* Banner com Informações do Laboratório Ativo */}
        {labData && (
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 p-4 rounded-2xl bg-white dark:bg-zinc-900 border border-slate-200 dark:border-zinc-800 shadow-sm">
            <div>
              <div className="flex items-center gap-2">
                <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse" />
                <h2 className="text-base font-bold text-slate-900 dark:text-white">
                  {labData.lab_name}
                </h2>
                <span className="text-xs text-slate-400 font-normal">
                  ({labData.floor})
                </span>
              </div>
              <p className="text-xs text-slate-500 dark:text-zinc-400 mt-0.5">
                Responsável técnico: <b className="text-slate-700 dark:text-zinc-300">{labData.responsible_person || 'Equipe de TI Senac'}</b> • Capacidade: <b>{labData.capacity} estações</b>
              </p>
            </div>
            <span className="text-xs px-3 py-1 rounded-full bg-blue-50 dark:bg-blue-950/50 text-[#004A99] dark:text-blue-300 border border-blue-200 dark:border-blue-800/50 font-medium self-start sm:self-auto">
              API FastAPI Online • 8000
            </span>
          </div>
        )}

        {/* Notificação de Erro se houver */}
        {errorMessage && (
          <div className="p-4 rounded-2xl bg-rose-50 dark:bg-rose-950/40 border border-rose-200 dark:border-rose-800 text-rose-700 dark:text-rose-300 flex items-center justify-between text-sm">
            <div className="flex items-center gap-2">
              <AlertTriangle className="w-5 h-5 shrink-0" />
              <span>{errorMessage}</span>
            </div>
            <button
              onClick={() => loadPanorama(currentLabId)}
              className="px-3 py-1 bg-rose-600 hover:bg-rose-700 text-white rounded-lg text-xs font-semibold"
            >
              Tentar novamente
            </button>
          </div>
        )}

        {/* Métricas e KPIs (Topo do Dashboard) */}
        {labData && (
          <section className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {/* Card Total e Taxa Operacional */}
            <div className="bg-white dark:bg-zinc-900 p-5 rounded-2xl border border-slate-200 dark:border-zinc-800 shadow-sm relative overflow-hidden">
              <div className="flex justify-between items-start">
                <div>
                  <p className="text-xs font-semibold text-slate-400 dark:text-zinc-500 uppercase tracking-wider">
                    Total no Laboratório
                  </p>
                  <h3 className="text-3xl font-extrabold text-slate-900 dark:text-white mt-1">
                    {labData.kpis.total_machines}{' '}
                    <span className="text-sm font-normal text-slate-400">PCs</span>
                  </h3>
                </div>
                <div className="p-3 bg-blue-50 dark:bg-blue-950/40 text-[#004A99] dark:text-blue-400 rounded-xl">
                  <Monitor className="w-5 h-5" />
                </div>
              </div>
              <div className="mt-4">
                <div className="flex justify-between text-xs mb-1.5 font-medium">
                  <span className="text-slate-500">Disponibilidade</span>
                  <span className="font-bold text-emerald-600 dark:text-emerald-400">
                    {labData.kpis.operational_rate}%
                  </span>
                </div>
                <div className="w-full bg-slate-100 dark:bg-zinc-800 rounded-full h-2 overflow-hidden">
                  <div
                    className="bg-emerald-500 h-2 rounded-full transition-all duration-700"
                    style={{ width: `${labData.kpis.operational_rate}%` }}
                  />
                </div>
              </div>
            </div>

            {/* Card Bom Estado */}
            <div className="bg-white dark:bg-zinc-900 p-5 rounded-2xl border border-slate-200 dark:border-zinc-800 shadow-sm">
              <div className="flex justify-between items-start">
                <div>
                  <p className="text-xs font-semibold text-slate-400 dark:text-zinc-500 uppercase tracking-wider">
                    Bom Estado
                  </p>
                  <h3 className="text-3xl font-extrabold text-emerald-600 dark:text-emerald-400 mt-1">
                    {labData.kpis.operational_count}
                  </h3>
                </div>
                <div className="p-3 bg-emerald-50 dark:bg-emerald-950/40 text-emerald-600 dark:text-emerald-400 rounded-xl">
                  <CheckCircle2 className="w-5 h-5" />
                </div>
              </div>
              <p className="mt-4 text-xs text-slate-500 dark:text-zinc-400 flex items-center gap-1 font-medium">
                100% operacionais para aulas
              </p>
            </div>

            {/* Card Em Manutenção */}
            <div className="bg-white dark:bg-zinc-900 p-5 rounded-2xl border border-slate-200 dark:border-zinc-800 shadow-sm">
              <div className="flex justify-between items-start">
                <div>
                  <p className="text-xs font-semibold text-slate-400 dark:text-zinc-500 uppercase tracking-wider">
                    Em Manutenção
                  </p>
                  <h3 className="text-3xl font-extrabold text-amber-500 mt-1">
                    {labData.kpis.maintenance_count}
                  </h3>
                </div>
                <div className="p-3 bg-amber-50 dark:bg-amber-950/40 text-amber-500 rounded-xl">
                  <AlertTriangle className="w-5 h-5" />
                </div>
              </div>
              <p className="mt-4 text-xs text-slate-500 dark:text-zinc-400">
                Aguardando peças ou reparo na bancada
              </p>
            </div>

            {/* Card Gargalos e Danificados */}
            <div className="bg-white dark:bg-zinc-900 p-5 rounded-2xl border border-slate-200 dark:border-zinc-800 shadow-sm">
              <div className="flex justify-between items-start">
                <div>
                  <p className="text-xs font-semibold text-slate-400 dark:text-zinc-500 uppercase tracking-wider">
                    Danificados / Obsoletos
                  </p>
                  <h3 className="text-3xl font-extrabold text-rose-500 mt-1">
                    {labData.kpis.damaged_count + labData.kpis.obsolete_count}
                  </h3>
                </div>
                <div className="p-3 bg-rose-50 dark:bg-rose-950/40 text-rose-500 rounded-xl">
                  <ShieldAlert className="w-5 h-5" />
                </div>
              </div>
              <p className="mt-4 text-xs text-slate-500 dark:text-zinc-400">
                {labData.kpis.damaged_count} Danificado(s) • {labData.kpis.obsolete_count} Obsoleto(s)
              </p>
            </div>
          </section>
        )}

        {/* Barra de Filtros e Busca */}
        <section className="bg-white dark:bg-zinc-900 p-4 rounded-2xl border border-slate-200 dark:border-zinc-800 shadow-sm flex flex-col md:flex-row gap-4 justify-between items-center">
          <div className="relative w-full md:w-96">
            <Search className="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" />
            <input
              type="text"
              placeholder="Buscar por patrimônio (ex: 024008) ou IP..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2.5 bg-slate-50 dark:bg-zinc-800/70 border border-slate-200 dark:border-zinc-700/80 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-[#004A99] dark:focus:ring-blue-500 transition-all placeholder:text-slate-400"
            />
          </div>

          <div className="flex items-center gap-1.5 w-full md:w-auto overflow-x-auto pb-1 md:pb-0">
            <span className="text-xs font-semibold text-slate-400 flex items-center gap-1.5 ml-1 mr-1">
              <SlidersHorizontal className="w-3.5 h-3.5" /> Filtrar:
            </span>
            {[
              { key: 'ALL', label: 'Todos' },
              { key: 'OPERATIONAL', label: '🟢 Bom Estado' },
              { key: 'MAINTENANCE', label: '🟡 Manutenção' },
              { key: 'DAMAGED', label: '🔴 Danificado' },
              { key: 'OBSOLETE', label: '⚪ Obsoleto' },
            ].map((f) => (
              <button
                key={f.key}
                onClick={() => setSelectedStatusFilter(f.key)}
                className={`px-3 py-1.5 rounded-lg text-xs font-semibold whitespace-nowrap transition-all ${
                  selectedStatusFilter === f.key
                    ? 'bg-[#004A99] text-white shadow-sm'
                    : 'bg-slate-100 dark:bg-zinc-800 text-slate-600 dark:text-zinc-400 hover:bg-slate-200 dark:hover:bg-zinc-700'
                }`}
              >
                {f.label}
              </button>
            ))}
          </div>
        </section>

        {/* Panorama Visual das Estações de Trabalho (Grid) */}
        <section>
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-lg font-extrabold text-slate-900 dark:text-white tracking-tight flex items-center gap-2">
              <span>Estações do Laboratório</span>
              <span className="text-xs font-bold px-2.5 py-0.5 rounded-full bg-slate-200 dark:bg-zinc-800 text-slate-700 dark:text-zinc-300">
                {filteredComputers.length} PCs
              </span>
            </h3>
            <span className="text-xs text-slate-400 hidden sm:inline">
              Clique em qualquer computador para ver detalhes e ações rápidas
            </span>
          </div>

          {isLoading && !labData ? (
            <div className="p-16 text-center bg-white dark:bg-zinc-900 rounded-3xl border border-slate-200 dark:border-zinc-800">
              <RefreshCw className="w-8 h-8 text-[#004A99] animate-spin mx-auto mb-3" />
              <p className="text-sm font-medium text-slate-600 dark:text-zinc-300">
                Carregando panorama das máquinas...
              </p>
            </div>
          ) : filteredComputers.length === 0 ? (
            <div className="bg-white dark:bg-zinc-900 p-12 text-center rounded-3xl border border-dashed border-slate-300 dark:border-zinc-800">
              <Monitor className="w-12 h-12 text-slate-300 dark:text-zinc-600 mx-auto mb-3" />
              <h4 className="font-semibold text-base">Nenhum computador encontrado</h4>
              <p className="text-sm text-slate-500 dark:text-zinc-400 mt-1">
                Tente ajustar os termos de busca ou selecionar outro filtro de status.
              </p>
            </div>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
              {filteredComputers.map((comp) => {
                const config = STATUS_CONFIG[comp.status];

                return (
                  <div
                    key={comp.id}
                    onClick={() => {
                      setSelectedComputer(comp);
                      setShowTicketForm(false);
                    }}
                    className={`group cursor-pointer bg-white dark:bg-zinc-900 p-5 rounded-2xl border border-slate-200 dark:border-zinc-800 shadow-sm transition-all duration-200 hover:-translate-y-1 hover:shadow-lg ${config.borderClass} ${config.bgGlow}`}
                  >
                    {/* Header do Card */}
                    <div className="flex justify-between items-start mb-3">
                      <div>
                        <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">
                          Patrimônio
                        </span>
                        <h4 className="text-lg font-black text-slate-900 dark:text-white tracking-tight group-hover:text-[#004A99] dark:group-hover:text-blue-400 transition-colors">
                          #{comp.patrimony}
                        </h4>
                      </div>
                      <span
                        className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-bold border ${config.badgeClass}`}
                      >
                        <span className={`w-2 h-2 rounded-full ${config.dotColor}`} />
                        {config.label}
                      </span>
                    </div>

                    {/* Especificações resumidas */}
                    <div className="space-y-1.5 text-xs text-slate-500 dark:text-zinc-400 pt-2 border-t border-slate-100 dark:border-zinc-800/80">
                      <div className="flex items-center justify-between">
                        <span className="flex items-center gap-1 text-slate-400">
                          <Wifi className="w-3.5 h-3.5" /> IP
                        </span>
                        <span className="font-mono font-semibold text-slate-700 dark:text-zinc-300">
                          {comp.ip_address || 'Não atribuído'}
                        </span>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="flex items-center gap-1 text-slate-400">
                          <Cpu className="w-3.5 h-3.5" /> Hardware
                        </span>
                        <span className="font-medium text-slate-700 dark:text-zinc-300 truncate max-w-[150px]">
                          {comp.specs.ram_gb}GB • {comp.specs.storage}
                        </span>
                      </div>
                    </div>

                    {/* Alerta de defeito/manutenção se houver */}
                    {comp.notes && (
                      <div className="mt-3 p-2 rounded-xl bg-amber-500/10 border border-amber-500/25 text-[11px] text-amber-700 dark:text-amber-400 flex items-start gap-1.5">
                        <AlertTriangle className="w-3.5 h-3.5 shrink-0 mt-0.5" />
                        <span className="line-clamp-1 font-medium">{comp.notes}</span>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          )}
        </section>
      </main>

      {/* Modal / Slide-Over de Detalhes da Máquina */}
      {selectedComputer && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-fade-in">
          <div className="bg-white dark:bg-zinc-900 w-full max-w-2xl rounded-3xl border border-slate-200 dark:border-zinc-800 shadow-2xl overflow-hidden animate-scale-up">
            {/* Header do Modal */}
            <div className="px-6 py-4 border-b border-slate-100 dark:border-zinc-800 flex justify-between items-center bg-slate-50/70 dark:bg-zinc-800/40">
              <div className="flex items-center gap-3">
                <div className="p-3 bg-[#004A99]/10 text-[#004A99] dark:text-blue-400 rounded-2xl">
                  <Monitor className="w-6 h-6" />
                </div>
                <div>
                  <div className="flex items-center gap-2">
                    <h3 className="text-xl font-black text-slate-900 dark:text-white">
                      Estação #{selectedComputer.patrimony}
                    </h3>
                    <span
                      className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-bold border ${
                        STATUS_CONFIG[selectedComputer.status].badgeClass
                      }`}
                    >
                      <span className={`w-2 h-2 rounded-full ${STATUS_CONFIG[selectedComputer.status].dotColor}`} />
                      {STATUS_CONFIG[selectedComputer.status].label}
                    </span>
                  </div>
                  <p className="text-xs text-slate-500 dark:text-zinc-400 mt-0.5">
                    {selectedComputer.hostname || `PC-LAB${currentLabId}`} • Laboratório {currentLabId} • Senac Ceilândia
                  </p>
                </div>
              </div>

              <button
                onClick={() => setSelectedComputer(null)}
                className="p-2 text-slate-400 hover:text-slate-600 dark:hover:text-white rounded-xl hover:bg-slate-100 dark:hover:bg-zinc-800 transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Notificação de sucesso no modal */}
            {actionSuccessNotice && (
              <div className="bg-emerald-500 text-white px-6 py-2.5 text-xs font-semibold flex items-center gap-2 animate-fade-in">
                <Check className="w-4 h-4" />
                {actionSuccessNotice}
              </div>
            )}

            <div className="p-6 space-y-6 max-h-[75vh] overflow-y-auto">
              {/* Informações de Rede e Posição */}
              <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 p-4 rounded-2xl bg-slate-50 dark:bg-zinc-800/40 border border-slate-200/80 dark:border-zinc-800 text-xs">
                <div>
                  <span className="text-slate-400 uppercase font-semibold text-[10px]">Endereço IP</span>
                  <p className="font-mono font-bold text-slate-800 dark:text-zinc-200 mt-0.5">
                    {selectedComputer.ip_address || '10.20.1.x'}
                  </p>
                </div>
                <div>
                  <span className="text-slate-400 uppercase font-semibold text-[10px]">Endereço MAC</span>
                  <p className="font-mono font-bold text-slate-800 dark:text-zinc-200 mt-0.5">
                    {selectedComputer.mac_address || '00:1A:2B:3C:xx:xx'}
                  </p>
                </div>
                <div>
                  <span className="text-slate-400 uppercase font-semibold text-[10px]">Posição na Sala</span>
                  <p className="font-bold text-slate-800 dark:text-zinc-200 mt-0.5">
                    {selectedComputer.grid_position
                      ? `Fileira ${selectedComputer.grid_position.row}, Mesa ${selectedComputer.grid_position.col}`
                      : 'Mesa padrão'}
                  </p>
                </div>
              </div>

              {/* Ficha Técnica de Hardware */}
              <div>
                <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2.5 flex items-center gap-1.5">
                  <Cpu className="w-4 h-4 text-[#004A99]" /> Especificações de Hardware
                </h4>
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                  <div className="p-3 bg-slate-50 dark:bg-zinc-800/40 rounded-2xl border border-slate-100 dark:border-zinc-800">
                    <span className="text-[10px] text-slate-400 uppercase font-bold">Processador</span>
                    <p className="text-xs font-bold text-slate-800 dark:text-zinc-200 mt-1">
                      {selectedComputer.specs.processor}
                    </p>
                  </div>
                  <div className="p-3 bg-slate-50 dark:bg-zinc-800/40 rounded-2xl border border-slate-100 dark:border-zinc-800">
                    <span className="text-[10px] text-slate-400 uppercase font-bold">Memória RAM</span>
                    <p className="text-xs font-bold text-slate-800 dark:text-zinc-200 mt-1">
                      {selectedComputer.specs.ram_gb} GB DDR4
                    </p>
                  </div>
                  <div className="p-3 bg-slate-50 dark:bg-zinc-800/40 rounded-2xl border border-slate-100 dark:border-zinc-800">
                    <span className="text-[10px] text-slate-400 uppercase font-bold">Armazenamento</span>
                    <p className="text-xs font-bold text-slate-800 dark:text-zinc-200 mt-1">
                      {selectedComputer.specs.storage}
                    </p>
                  </div>
                  <div className="p-3 bg-slate-50 dark:bg-zinc-800/40 rounded-2xl border border-slate-100 dark:border-zinc-800">
                    <span className="text-[10px] text-slate-400 uppercase font-bold">Sistema Operacional</span>
                    <p className="text-xs font-bold text-slate-800 dark:text-zinc-200 mt-1 truncate">
                      {selectedComputer.specs.operating_system}
                    </p>
                  </div>
                </div>
              </div>

              {/* Ações Rápidas de 1-Clique */}
              <div>
                <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2 flex items-center justify-between">
                  <span>Ações Rápidas (Alterar Status em 1-Clique)</span>
                  <span className="text-[11px] font-normal text-slate-400">Registrado via API</span>
                </h4>
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
                  {(
                    [
                      { key: 'OPERATIONAL', label: '🟢 Bom Estado', reason: 'Equipamento testado e operacional' },
                      { key: 'MAINTENANCE', label: '🟡 Em Manutenção', reason: 'Encaminhado para bancada técnica' },
                      { key: 'DAMAGED', label: '🔴 Danificado', reason: 'Falha ou defeito de hardware constatado' },
                      { key: 'OBSOLETE', label: '⚪ Obsoleto', reason: 'Equipamento depreciado para substituição' },
                    ] as const
                  ).map((action) => (
                    <button
                      key={action.key}
                      onClick={() => handleQuickStatus(action.key, action.reason)}
                      disabled={isSubmittingAction || selectedComputer.status === action.key}
                      className={`px-3 py-2.5 rounded-xl text-xs font-bold border transition-all text-center ${
                        selectedComputer.status === action.key
                          ? 'opacity-40 cursor-not-allowed border-slate-300 dark:border-zinc-700 bg-slate-100 dark:bg-zinc-800'
                          : 'hover:scale-[1.02] active:scale-95 border-slate-200 dark:border-zinc-700 hover:border-[#004A99] dark:hover:border-blue-400 bg-white dark:bg-zinc-800 shadow-sm'
                      }`}
                    >
                      {action.label}
                    </button>
                  ))}
                </div>
              </div>

              {/* Histórico e Chamados Técnicos */}
              <div>
                <div className="flex justify-between items-center mb-3">
                  <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
                    <History className="w-4 h-4 text-[#004A99]" /> Histórico de Manutenção e Auditoria
                  </h4>
                  <button
                    onClick={() => setShowTicketForm(!showTicketForm)}
                    className="text-xs font-semibold text-[#004A99] dark:text-blue-400 hover:underline flex items-center gap-1"
                  >
                    <PlusCircle className="w-3.5 h-3.5" />
                    {showTicketForm ? 'Cancelar Chamado' : 'Adicionar Chamado / Nota'}
                  </button>
                </div>

                {/* Formulário para novo chamado */}
                {showTicketForm && (
                  <form
                    onSubmit={handleCreateTicket}
                    className="p-4 rounded-2xl bg-blue-50/50 dark:bg-zinc-800/80 border border-blue-200 dark:border-zinc-700 mb-4 space-y-3 animate-scale-up"
                  >
                    <h5 className="text-xs font-bold text-[#004A99] dark:text-blue-300">
                      Novo Chamado para o PC #{selectedComputer.patrimony}
                    </h5>
                    <input
                      type="text"
                      placeholder="Título (ex: Substituição de pasta térmica)"
                      value={ticketTitle}
                      onChange={(e) => setTicketTitle(e.target.value)}
                      required
                      className="w-full px-3 py-2 text-xs rounded-xl bg-white dark:bg-zinc-900 border border-slate-200 dark:border-zinc-700 focus:outline-none focus:ring-2 focus:ring-[#004A99]"
                    />
                    <textarea
                      placeholder="Descrição técnica detalhada..."
                      rows={2}
                      value={ticketDesc}
                      onChange={(e) => setTicketDesc(e.target.value)}
                      required
                      className="w-full px-3 py-2 text-xs rounded-xl bg-white dark:bg-zinc-900 border border-slate-200 dark:border-zinc-700 focus:outline-none focus:ring-2 focus:ring-[#004A99]"
                    />
                    <div className="flex justify-end gap-2">
                      <button
                        type="button"
                        onClick={() => setShowTicketForm(false)}
                        className="px-3 py-1.5 text-xs text-slate-500 rounded-lg hover:bg-slate-200 dark:hover:bg-zinc-700"
                      >
                        Cancelar
                      </button>
                      <button
                        type="submit"
                        disabled={isSubmittingAction}
                        className="px-4 py-1.5 bg-[#004A99] hover:bg-blue-800 text-white rounded-lg text-xs font-semibold flex items-center gap-1.5 shadow-sm"
                      >
                        <Send className="w-3.5 h-3.5" />
                        Registrar Chamado
                      </button>
                    </div>
                  </form>
                )}

                {/* Timeline de Registros */}
                {selectedComputer.history.length === 0 ? (
                  <div className="p-4 rounded-2xl bg-slate-50 dark:bg-zinc-800/40 border border-slate-100 dark:border-zinc-800 text-center text-xs text-slate-400 italic">
                    Nenhuma manutenção anterior registrada para esta máquina.
                  </div>
                ) : (
                  <div className="space-y-2.5">
                    {selectedComputer.history.map((log) => (
                      <div
                        key={log.id}
                        className="p-3 rounded-2xl bg-slate-50 dark:bg-zinc-800/40 border border-slate-100 dark:border-zinc-800 text-xs flex gap-3"
                      >
                        <div className="w-2 h-2 rounded-full bg-[#004A99] mt-1.5 shrink-0 shadow-sm" />
                        <div className="flex-1">
                          <div className="flex justify-between items-center">
                            <h5 className="font-bold text-slate-800 dark:text-zinc-200">
                              {log.title}
                            </h5>
                            <span className="text-[10px] text-slate-400 font-mono">
                              {new Date(log.created_at).toLocaleDateString('pt-BR')}
                            </span>
                          </div>
                          <p className="text-slate-600 dark:text-zinc-400 mt-1 text-[11px]">
                            {log.description}
                          </p>
                          <span className="inline-block text-[10px] font-semibold text-slate-400 mt-1.5">
                            Técnico: {log.technician_name} • {log.action_type}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>

            {/* Rodapé do Modal */}
            <div className="px-6 py-3.5 bg-slate-50 dark:bg-zinc-800/50 border-t border-slate-100 dark:border-zinc-800 flex justify-between items-center">
              <span className="text-xs text-slate-400 font-mono">
                Patrimônio #{selectedComputer.patrimony}
              </span>
              <button
                onClick={() => setSelectedComputer(null)}
                className="px-5 py-2 text-xs font-bold rounded-xl bg-[#004A99] hover:bg-blue-800 text-white transition-colors shadow-sm"
              >
                Concluir Visualização
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
