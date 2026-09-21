@echo off
title Senac TechLab - Inicializador Full-Stack
echo ============================================================
echo      INICIANDO SENAC TECHLAB - GESTAO DE ATIVOS DE TI
echo ============================================================
echo.

echo 1. Iniciando Back-end (FastAPI)...
start "Senac TechLab - Backend API" cmd /k "cd /d %~dp0backend && .venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload"

timeout /t 3 /nobreak > nul

echo 2. Iniciando Front-end (React + Vite)...
start "Senac TechLab - Frontend Dashboard" cmd /k "cd /d %~dp0frontend && npm run dev -- --host 127.0.0.1 --port 5173"

echo.
echo ============================================================
echo   Aplicacao em execucao!
echo   Front-end: http://127.0.0.1:5173/
echo   Back-end Docs: http://127.0.0.1:8000/docs
echo ============================================================
pause
