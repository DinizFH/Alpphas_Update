#Funções de CRUD de clientes

from typing import List, Dict, Optional
from db import get_connection


def listar_clientes() -> List[Dict]:
    """
    Retorna todos os clientes cadastrados.
    """
    sql = "SELECT id, nome, criado_em FROM clientes ORDER BY nome ASC"

    with get_connection() as conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(sql)
        rows = cursor.fetchall()
    return rows


def criar_cliente(nome: str) -> int:
    """
    Insere um novo cliente e retorna o ID gerado.
    """
    sql = "INSERT INTO clientes (nome) VALUES (%s)"

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(sql, (nome,))
        conn.commit()
        return cursor.lastrowid


def buscar_cliente_por_id(cliente_id: int) -> Optional[Dict]:
    """
    Busca um cliente pelo ID.
    """
    sql = "SELECT id, nome, criado_em FROM clientes WHERE id = %s"

    with get_connection() as conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(sql, (cliente_id,))
        row = cursor.fetchone()
    return row


def excluir_cliente(cliente_id: int) -> None:
    """
    Exclui um cliente pelo ID.
    """
    sql = "DELETE FROM clientes WHERE id = %s"

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(sql, (cliente_id,))
        conn.commit()
