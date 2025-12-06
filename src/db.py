#Configuraçõ de conexão com o banco de dados
import mysql.connector
from mysql.connector import Error

DB_CONFIG = {
    "host": "localhost",
    "user": "root", 
    "password": "Diniz@3582",
    "database": "alpphas_update",
}


def get_connection():
    """
    Abre uma conexão com o banco de dados MySQL.
    Use com 'with get_connection() as conn:'.
    """
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Error as e:
        print(f"[ERRO] Não foi possível conectar ao banco: {e}")
        raise
