# src/aplicativos_repo.py
from typing import List, Dict
from db import get_connection


def listar_aplicativos_resumo() -> List[Dict]:
    """
    Lista aplicativos com quantidade de versões e última versão cadastrada.
    """
    sql = """
        SELECT
            a.id,
            a.nome,
            a.criado_em,
            COUNT(v.id) AS total_versoes,
            MAX(v.versao) AS ultima_versao
        FROM aplicativos a
        LEFT JOIN aplicativos_versoes v ON v.aplicativo_id = a.id
        GROUP BY a.id, a.nome, a.criado_em
        ORDER BY a.nome ASC
    """

    with get_connection() as conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(sql)
        rows = cursor.fetchall()
    return rows


def criar_aplicativo(nome: str) -> int:
    """
    Cria um novo aplicativo (tipo) e retorna o ID.
    """
    sql = "INSERT INTO aplicativos (nome) VALUES (%s)"

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(sql, (nome,))
        conn.commit()
        return cursor.lastrowid


def criar_versao(aplicativo_id: int, versao: str, arquivo_local: str, padrao: bool = True) -> int:
    """
    Cria um registro de versão de aplicativo.
    Se padrao=True, desmarca outras versões padrão desse aplicativo.
    """
    with get_connection() as conn:
        cursor = conn.cursor()

        if padrao:
            cursor.execute(
                "UPDATE aplicativos_versoes SET padrao = 0 WHERE aplicativo_id = %s",
                (aplicativo_id,),
            )

        sql = """
            INSERT INTO aplicativos_versoes (aplicativo_id, versao, arquivo_local, padrao)
            VALUES (%s, %s, %s, %s)
        """
        cursor.execute(sql, (aplicativo_id, versao, arquivo_local, int(padrao)))
        conn.commit()
        return cursor.lastrowid


def excluir_aplicativo(aplicativo_id: int) -> None:
    """
    Exclui um aplicativo (todas as versões serão excluídas via cascade).
    """
    sql = "DELETE FROM aplicativos WHERE id = %s"

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(sql, (aplicativo_id,))
        conn.commit()
