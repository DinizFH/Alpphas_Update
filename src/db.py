import os
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv

# Carrega variáveis do arquivo .env
load_dotenv()

def get_connection():
    try:
        conn = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASS"),
            database=os.getenv("DB_NAME"),
        )
        return conn

    except Error as e:
        print(f"[ERRO] Não foi possível conectar ao banco: {e}")
        raise e
