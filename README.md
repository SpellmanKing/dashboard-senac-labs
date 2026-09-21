# Senac TechLab - Dashboard de Gestão de Ativos de TI 🖥️

Aplicação Full-Stack moderna e de alta performance desenvolvida para o monitoramento, inventário e gestão de ativos de informática dos **Laboratórios de Informática do Senac Ceilândia** (Laboratórios 1, 2 e 3 com 86 computadores mapeados).

---

## 🚀 Tecnologias Utilizadas

### Back-end
- **Python 3.13** com **FastAPI** (alta performance assíncrona, validação Pydantic v2).
- **SQLAlchemy 2.0** (ORM moderno com tipagem `Mapped` e `mapped_column`).
- **SQLite (aiosqlite)** para execução local imediata out-of-the-box e suporte total a **PostgreSQL** via variável de ambiente `DATABASE_URL`.
- **Swagger / OpenAPI** integrado automaticamente em `/docs`.

### Front-end
- **React 18** com **TypeScript** e **Vite**.
- **Tailwind CSS** com suporte nativo a **Dark Mode** e paleta visual com as cores do Senac (Azul `#004A99` e Laranja `#F6821F`).
- **Lucide Icons** para ícones modernos e microinterações.

---

## ⚙️ Como Executar

### Opção 1: Inicialização em 1-Clique no Windows
Basta dar um duplo clique no arquivo:
```cmd
start_app.bat
```
Ele iniciará a API FastAPI na porta `8000` e o painel React na porta `5173`.

---

### Opção 2: Execução Manual

#### 1. Back-end (FastAPI):
```bash
cd backend
# Ativar ambiente virtual
.\.venv\Scripts\activate
# Iniciar servidor FastAPI com recarregamento automático
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
- Acesse a documentação interativa: **[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)**

#### 2. Front-end (React + Vite):
```bash
cd frontend
npm run dev
```
- Acesse o dashboard no navegador: **[http://127.0.0.1:5173/](http://127.0.0.1:5173/)**

---

## 📊 Funcionalidades do Dashboard

1. **Mapeamento de Ambientes:**
   - Alternância imediata entre os **Laboratórios 1, 2 e 3**.
2. **Métricas e KPIs em Tempo Real:**
   - Total de máquinas, computadores em Bom Estado, Em Manutenção, Danificados e Obsoletos.
   - Taxa de disponibilidade calculada em tempo real com barra de progresso.
3. **Filtros e Busca Avançada:**
   - Campo de busca instantânea por **número de patrimônio** (ex: `024008`, `024029`) ou **endereço IP**.
   - Filtros de status (🟢 Bom Estado, 🟡 Em Manutenção, 🔴 Danificado, ⚪ Obsoleto).
4. **Modal de Detalhes da Estação:**
   - Ficha técnica completa de hardware (Processador, Memória RAM, Armazenamento, SO).
   - Endereço IP, MAC e fileira/mesa na sala.
   - Linha do tempo de histórico e auditoria de chamados.
   - **Ações Rápidas de 1-Clique:** Botões para alterar o status da máquina diretamente via API, registrando o log técnico automaticamente.
   - Formulário para abertura de chamados técnicos internos.
5. **Legado:**
   - A versão anterior em Streamlit foi preservada em `legacy_streamlit_app.py`.
