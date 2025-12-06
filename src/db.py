import os
import sys
from pathlib import Path

import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv


def carregar_env():
    """
    Procura o .env em vários lugares, tanto em modo dev quanto no executável:

    1) Pasta onde o PyInstaller extrai os arquivos (_MEIPASS)
    2) Pasta do próprio db.py (src)
    3) Pasta pai (raiz do projeto)
    4) Diretório atual (cwd)
    """
    base_paths = []

    # 1) Executável PyInstaller (_MEIPASS)
    if getattr(sys, "_MEIPASS", None):
        base_paths.append(Path(sys._MEIPASS))

    # 2) Pasta do arquivo db.py (src)
    base_paths.append(Path(__file__).resolve().parent)

    # 3) Pasta pai (raiz do projeto em modo dev)
    base_paths.append(Path(__file__).resolve().parent.parent)

    # 4) Diretório atual
    base_paths.append(Path.cwd())

    for base in base_paths:
        env_path = base / ".env"
        if env_path.exists():
            load_dotenv(env_path)
            return

    # Fallback: tenta do jeito padrão
    load_dotenv()


# Carrega o .env
carregar_env()

# Lê as variáveis com defaults seguros
DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_PORT = int(os.getenv("DB_PORT", "3307"))
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "alpphas_update")


def get_connection():
    try:
        conn = mysql.connector.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
        )
        return conn
    except Error as e:
        print(f"[ERRO] Não foi possivel conectar ao banco: {e}")
        raise
