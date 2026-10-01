import streamlit as st
import pandas as pd
import plotly.express as px
import json
import os

# --- CONFIGURAÇÃO INICIAL ---
st.set_page_config(page_title="Gestão Lab Senac", layout="wide", page_icon="🖥️")

# Arquivos de "banco de dados" local
ARQUIVO_SALAS = 'db_salas.json'
ARQUIVO_DEFEITOS = 'db_defeitos.json'
ARQUIVO_INVENTARIO = 'inventario.json'

# --- FUNÇÕES DE PERSISTÊNCIA ---
def carregar_dados():
    # 1. Carregar Salas
    if os.path.exists(ARQUIVO_SALAS):
        df_salas = pd.read_json(ARQUIVO_SALAS)
    else:
        # Dados padrão se o arquivo não existir
        df_salas = pd.DataFrame({
            'Sala': ['Lab. Informática 1', 'Lab. Informática 2', 'Lab. Informática 3'],
            'Status': ['Ocupada', 'Livre', 'Ocupada'],
            'Responsável': ['Prof. João', '', 'José Chaves'],
            'Capacidade': [28, 28, 30]
        })

    # 2. Carregar Defeitos
    if os.path.exists(ARQUIVO_DEFEITOS):
        with open(ARQUIVO_DEFEITOS, 'r') as f:
            maquinas_defeito = json.load(f)
    else:
        maquinas_defeito = {}
    
    return df_salas, maquinas_defeito

def carregar_inventario():
    # Tenta carregar do arquivo JSON externo (Melhoria 2)
    if os.path.exists(ARQUIVO_INVENTARIO):
        with open(ARQUIVO_INVENTARIO, 'r') as f:
            return json.load(f)
    else:
        # BACKUP: Caso o arquivo json não exista, usa estes dados para não quebrar o app
        return {
            'Lab. Informática 1': ['024008', '023402', '024398', '024019', '024020', '023999'],
            'Lab. Informática 2': ['024016', '023996', '023989', '024009', '024023', '023983'],
            'Lab. Informática 3': ['033216', '033217', '033218', '033219', '033220', '033221']
        }

def salvar_tudo():
    # Salva o DataFrame de salas
    st.session_state.db_salas.to_json(ARQUIVO_SALAS)
    # Salva o Dicionário de defeitos
    with open(ARQUIVO_DEFEITOS, 'w') as f:
        json.dump(st.session_state.maquinas_defeito, f)

# --- ESTILIZAÇÃO CSS ---
st.markdown("""
    <style>
    [data-testid="stMetric"] { background-color: #1E1E1E; padding: 15px; border-radius: 10px; border: 1px solid #333; }
    [data-testid="stMetricValue"] { color: #FFFFFF !important; font-weight: bold; }
    [data-testid="stMetricLabel"] { color: #AAAAAA !important; }

    .sala-card {
        padding: 20px;
        border-radius: 12px;
        background-color: #FFFFFF;
        margin-bottom: 20px;
        border-left: 8px solid #004A99;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    .sala-card h3, .sala-card p, .sala-card b { color: #1A1A1A !important; margin: 5px 0; }
    .resp-vazio { color: #888888 !important; font-style: italic; }
    .warning-text { color: #dc3545 !important; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# --- INICIALIZAÇÃO DE DADOS ---
patrimonios_reais = carregar_inventario()

if 'db_salas' not in st.session_state:
    st.session_state.db_salas, st.session_state.maquinas_defeito = carregar_dados()

# --- SIDEBAR ---
with st.sidebar:
    st.title("⚙️ Painel de Controle")
    
    # 1. Busca
    st.subheader("🔍 Localizador de Patrimônio")
    search = st.text_input("Consultar número", placeholder="Ex: 024008")
    if search:
        found_sala = next((s for s, lista in patrimonios_reais.items() if search in lista), None)
        if found_sala:
            st.success(f"📍 Encontrado no **{found_sala}**")
        else:
            st.error("❌ Não encontrado.")

    st.divider()

    # 2. Manutenção
    st.subheader("🔧 Manutenção de Máquinas")
    pat_def = st.text_input("Patrimônio com Defeito", key="def_input")
    obs_def = st.text_area("Descrição do problema")
    
    col_def1, col_def2 = st.columns(2)
    
    # BOTÃO: Marcar Defeito
    if col_def1.button("Marcar Defeito"):
        if pat_def:
            found_s = next((s for s, l in patrimonios_reais.items() if pat_def in l), None)
            if found_s:
                st.session_state.maquinas_defeito[pat_def] = {'defeito': obs_def, 'sala': found_s}
                salvar_tudo() # <--- SALVA NO ARQUIVO
                st.success(f"Registrado no {found_s}")
                st.rerun()
            else:
                st.warning("Patrimônio não mapeado no inventário.")
        else:
            st.warning("Digite um patrimônio.")

    # BOTÃO: Liberar Máquina
    if col_def2.button("Liberar Máquina"):
        if pat_def in st.session_state.maquinas_defeito:
            del st.session_state.maquinas_defeito[pat_def]
            salvar_tudo() # <--- SALVA NO ARQUIVO
            st.success("Máquina liberada!")
            st.rerun()
        else:
            st.warning("Esta máquina não consta como defeituosa.")

    st.divider()

    # 3. Editar Sala
    st.subheader("📝 Editar Laboratório")
    sala_edit = st.selectbox("Selecionar Sala", st.session_state.db_salas['Sala'])
    status_edit = st.selectbox("Alterar Status", ["Livre", "Ocupada", "Manutenção"])
    resp_edit = st.text_input("Novo Responsável")
    
    # BOTÃO: Salvar Alterações de Sala
    if st.button("Salvar Alterações"):
        idx = st.session_state.db_salas.index[st.session_state.db_salas['Sala'] == sala_edit][0]
        st.session_state.db_salas.at[idx, 'Status'] = status_edit
        # Lógica: Se Livre, limpa o responsável
        st.session_state.db_salas.at[idx, 'Responsável'] = "" if status_edit == "Livre" else resp_edit
        
        salvar_tudo() # <--- SALVA NO ARQUIVO
        st.success("Status atualizado!")
        st.rerun()

# --- LAYOUT PRINCIPAL ---
st.title("🖥️ Gestão de Laboratórios - Senac Ceilândia")

# Métricas
m1, m2, m3, m4 = st.columns(4)
total_pcs = sum(len(lista) for lista in patrimonios_reais.values())
m1.metric("Máquinas Totais", total_pcs)
m2.metric("Salas Livres", len(st.session_state.db_salas[st.session_state.db_salas['Status'] == 'Livre']))
m3.metric("Máquinas em Reparo", len(st.session_state.maquinas_defeito))
m4.metric("Andar", "1º Pavimento")

st.divider()

col_cards, col_side = st.columns([1.6, 1])

with col_cards:
    st.subheader("📍 Status em Tempo Real")
    for _, row in st.session_state.db_salas.iterrows():
        # Filtra defeitos da sala atual
        bugs = {k: v for k, v in st.session_state.maquinas_defeito.items() if v['sala'] == row['Sala']}
        
        # Definição de Cores e Ícones
        cor = "#28a745" if row['Status'] == "Livre" else "#dc3545" if row['Status'] == "Ocupada" else "#ffc107"
        exibir_resp = row['Responsável'] if row['Responsável'] else "Sala Disponível"
        classe_resp = "" if row['Responsável'] else "class='resp-vazio'"
        
        # Alerta visual (Melhoria 3)
        icone_alerta = "🔴" if len(bugs) > 0 else "🟢"
        texto_defeitos = f"<span style='color:#dc3545; font-weight:bold'>⚠️ {len(bugs)} computador(es) com defeito</span>" if len(bugs) > 0 else "<span style='color:#28a745'>Nenhum defeito reportado</span>"

        st.markdown(f"""
            <div class="sala-card">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <h3 style="margin:0;">{row['Sala']}</h3>
                    <div style="font-size:1.5em;">{icone_alerta}</div>
                </div>
                <p><span style="color:{cor};">●</span> <b>{row['Status']}</b></p>
                <p {classe_resp}>👤 Resp: <b>{exibir_resp}</b></p>
                <hr style="border: 0; border-top: 1px solid #eee; margin: 10px 0;">
                <p>📦 Capacidade: <b>{row['Capacidade']} PCs</b></p>
                <p>{texto_defeitos}</p>
            </div>
        """, unsafe_allow_html=True)
        
        with st.expander(f"Ver Inventário - {row['Sala']}"):
            lista_patrimonios = patrimonios_reais.get(row['Sala'], [])
            if not lista_patrimonios:
                st.info("Lista de patrimônios vazia ou não carregada.")
            else:
                for p in lista_patrimonios:
                    if p in st.session_state.maquinas_defeito:
                        st.error(f"❌ {p} - {st.session_state.maquinas_defeito[p]['defeito']}")
                    else:
                        st.write(f"✅ {p}")

with col_side:
    st.subheader("📊 Visão de Ocupação")
    fig = px.pie(st.session_state.db_salas, names='Status', color='Status',
                 color_discrete_map={'Livre':'#28a745', 'Ocupada':'#dc3545', 'Manutenção':'#ffc107'})
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color="white", margin=dict(t=0, b=0, l=0, r=0))
    st.plotly_chart(fig, use_container_width=True)
    
    st.divider()
    st.subheader("📋 Resumo de Manutenção")
    if st.session_state.maquinas_defeito:
        for p, info in st.session_state.maquinas_defeito.items():
            st.warning(f"**PC {p}** ({info['sala']}):\n{info['defeito']}")
    else:
        st.success("Todos os laboratórios operando 100%!")