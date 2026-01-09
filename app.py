import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Configuração da Página e Estilo
st.set_page_config(page_title="Gestão Lab Senac", layout="wide", page_icon="🖥️")

st.markdown("""
    <style>
    /* Estilo das Métricas */
    [data-testid="stMetric"] { background-color: #1E1E1E; padding: 15px; border-radius: 10px; border: 1px solid #333; }
    [data-testid="stMetricValue"] { color: #FFFFFF !important; font-weight: bold; }
    [data-testid="stMetricLabel"] { color: #AAAAAA !important; }

    /* Estilo dos Cards das Salas */
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

# 2. Base de Dados de Patrimônios (Listas Reais dos seus Desenhos)
patrimonios_reais = {
    'Lab. Informática 1': [
        '024008', '023402', '024398', '024019', '024020', '023999', '023972', '023968',
        '024419', '023977', '024021', '024007', '024392', '023994', '024005', '024027',
        '024006', '024001', '024022', '023997', '024010', '023966', '024024', '024002',
        '024000', '023987', '024029', '023975'
    ],
    'Lab. Informática 2': [
        '024016', '023996', '023989', '024009', '024023', '023983', '023992', '023991',
        '023974', '023990', '023985', '023979', '024014', '024013', '023981', '023973',
        '023998', '024003', '024028', '023963', '024025', '023982', '024026', '023978',
        '023976', '023980', '024012', '024015'
    ],
    'Lab. Informática 3': [
        '033216', '033217', '033218', '033219', '033220', '033221', '033222', '033223',
        '033224', '033225', '033226', '033227', '033233', '033232', '033231', '033230',
        '033229', '033228', '033245', '033244', '033243', '033242', '033241', '033240',
        '033239', '033238', '033237', '033236', '033235', '033234'
    ]
}

# 3. Inicialização do Estado da Sessão (Persistence)
if 'db_salas' not in st.session_state:
    st.session_state.db_salas = pd.DataFrame({
        'Sala': ['Lab. Informática 1', 'Lab. Informática 2', 'Lab. Informática 3'],
        'Status': ['Ocupada', 'Livre', 'Ocupada'],
        'Responsável': ['Prof. João', '', 'José Chaves'],
        'Capacidade': [28, 28, 30]
    })

if 'maquinas_defeito' not in st.session_state:
    # Adicionando dado real do seu relatório de Janeiro
    st.session_state.maquinas_defeito = {
        '024029': {'defeito': 'Lentidão extrema (Processador obsoleto)', 'sala': 'Lab. Informática 1'}
    }

# 4. Sidebar: Administração, Localização e Manutenção
with st.sidebar:
    st.title("⚙️ Painel de Controle")
    
    # Função de Localização de Patrimônio
    st.subheader("🔍 Localizador de Patrimônio")
    search = st.text_input("Consultar número", placeholder="Ex: 024008")
    if search:
        found_sala = next((s for s, lista in patrimonios_reais.items() if search in lista), None)
        if found_sala:
            st.success(f"📍 Encontrado no **{found_sala}**")
        else:
            st.error("❌ Não encontrado.")

    st.divider()

    # Função de Registro de Defeito com Localização Automática
    st.subheader("🔧 Manutenção de Máquinas")
    pat_def = st.text_input("Patrimônio com Defeito", key="def_input")
    obs_def = st.text_area("Descrição do problema")
    
    col_def1, col_def2 = st.columns(2)
    if col_def1.button("Marcar Defeito"):
        if pat_def:
            found_s = next((s for s, l in patrimonios_reais.items() if pat_def in l), None)
            if found_s:
                st.session_state.maquinas_defeito[pat_def] = {'defeito': obs_def, 'sala': found_s}
                st.success(f"Registrado no {found_s}")
                st.rerun()
            else:
                st.warning("Patrimônio não mapeado.")

    if col_def2.button("Liberar Máquina"):
        if pat_def in st.session_state.maquinas_defeito:
            del st.session_state.maquinas_defeito[pat_def]
            st.rerun()

    st.divider()

    # Edição de Sala (Com limpeza automática de responsável)
    st.subheader("📝 Editar Laboratório")
    sala_edit = st.selectbox("Selecionar Sala", st.session_state.db_salas['Sala'])
    status_edit = st.selectbox("Alterar Status", ["Livre", "Ocupada", "Manutenção"])
    resp_edit = st.text_input("Novo Responsável")
    
    if st.button("Salvar Alterações"):
        idx = st.session_state.db_salas.index[st.session_state.db_salas['Sala'] == sala_edit][0]
        st.session_state.db_salas.at[idx, 'Status'] = status_edit
        # Lógica: Se Livre, limpa o responsável automaticamente
        st.session_state.db_salas.at[idx, 'Responsável'] = "" if status_edit == "Livre" else resp_edit
        st.rerun()

# 5. Layout Principal
st.title("🖥️ Gestão de Laboratórios - Senac Ceilândia")

# Métricas Superiores
m1, m2, m3, m4 = st.columns(4)
m1.metric("Máquinas Totais", "86")
m2.metric("Salas Livres", len(st.session_state.db_salas[st.session_state.db_salas['Status'] == 'Livre']))
m3.metric("Máquinas em Reparo", len(st.session_state.maquinas_defeito))
m4.metric("Andar", "1º Pavimento")

st.divider()

# Colunas de Cards e Gráfico
col_cards, col_side = st.columns([1.6, 1])

with col_cards:
    st.subheader("📍 Status em Tempo Real")
    for _, row in st.session_state.db_salas.iterrows():
        # Filtra defeitos da sala atual
        bugs = {k: v for k, v in st.session_state.maquinas_defeito.items() if v['sala'] == row['Sala']}
        cor = "#28a745" if row['Status'] == "Livre" else "#dc3545" if row['Status'] == "Ocupada" else "#ffc107"
        exibir_resp = row['Responsável'] if row['Responsável'] else "Sala Disponível"
        classe_resp = "" if row['Responsável'] else "class='resp-vazio'"

        st.markdown(f"""
            <div class="sala-card">
                <h3>{row['Sala']}</h3>
                <p><span style="color:{cor};">●</span> <b>{row['Status']}</b></p>
                <p {classe_resp}>👤 Resp: <b>{exibir_resp}</b></p>
                <p>📦 Total: <b>{row['Capacidade']} PCs</b> | ⚠️ Defeitos: <b class="warning-text">{len(bugs)}</b></p>
            </div>
        """, unsafe_allow_html=True)
        
        with st.expander(f"Inventário Completo - {row['Sala']}"):
            # Exibe lista real e destaca as que estão com defeito
            for p in patrimonios_reais[row['Sala']]:
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
            st.warning(f"**PC {p}** ({info['sala']}): {info['defeito']}")
    else:
        st.success("Tudo operando normalmente!")