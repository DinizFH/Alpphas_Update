from typing import List, Dict
from db import get_connection


def listar_equipamentos() -> List[Dict]:
    """
    Lista equipamentos com nome do cliente.

    Observação:
    - As colunas do banco são:
      nome_modelo, path_cadastros, path_mapas, path_pontofixo
    - Aqui fazemos alias (AS ...) para nomes mais amigáveis
      usados pela interface: nome, pasta_cadastros, etc.
    """
    sql = """
        SELECT
            e.id,
            c.nome AS cliente_nome,
            e.nome_modelo AS nome,
            e.path_cadastros AS pasta_cadastros,
            e.path_mapas AS pasta_mapas,
            e.path_pontofixo AS pasta_ponto_fixo,
            e.criado_em
        FROM equipamentos e
        JOIN clientes c ON c.id = e.cliente_id
        ORDER BY c.nome ASC, e.nome_modelo ASC
    """

    with get_connection() as conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(sql)
        return cursor.fetchall()


def criar_equipamento(
    cliente_id: int,
    nome: str,
    pasta_cadastros: str,
    pasta_mapas: str,
    pasta_ponto_fixo: str,
    tipo: str | None = None,
) -> int:
    """
    Cria um equipamento vinculado a um cliente.

    Mapeando:
    - nome           -> nome_modelo
    - pasta_*        -> path_*
    """
    sql = """
        INSERT INTO equipamentos
            (cliente_id, nome_modelo, tipo, path_cadastros, path_mapas, path_pontofixo)
        VALUES (%s, %s, %s, %s, %s, %s)
    """

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            sql,
            (
                cliente_id,
                nome,
                tipo,
                pasta_cadastros,
                pasta_mapas,
                pasta_ponto_fixo,
            ),
        )
        conn.commit()
        return cursor.lastrowid


def excluir_equipamento(equipamento_id: int) -> None:
    sql = "DELETE FROM equipamentos WHERE id = %s"

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(sql, (equipamento_id,))
        conn.commit()
