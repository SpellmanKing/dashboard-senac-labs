import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import engine, Base, AsyncSessionLocal
from app.core.seed import seed_initial_data
from app.api.v1.router import api_router

# Configuração de Logs
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("senac_backend")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Inicialização: Cria tabelas se não existirem
    logger.info("Verificando e criando tabelas no banco de dados...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Executa Seed Inicial com os dados reais do Senac
    async with AsyncSessionLocal() as session:
        await seed_initial_data(session)

    logger.info("🚀 Back-end Senac TechLab iniciado com sucesso!")
    yield
    # Finalização
    await engine.dispose()
    logger.info("Conexões com o banco de dados encerradas.")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="API de Gestão de Ativos de TI para os Laboratórios de Informática do Senac",
    lifespan=lifespan
)

# Configuração de CORS para permitir acesso do React / Vite
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rotas
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/", tags=["Health"])
async def root():
    return {
        "app": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "online",
        "docs": "/docs"
    }

@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "healthy"}
