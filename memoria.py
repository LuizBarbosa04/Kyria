import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
BANCO = BASE_DIR / "memoria.db"


def conectar():
    return sqlite3.connect(BANCO)


def criar_banco():
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS conversas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role TEXT NOT NULL,
            content TEXT NOT NULL
        )
        """
    )

    conexao.commit()
    conexao.close()


def salvar_mensagem(role, content):
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute(
        """
        INSERT INTO conversas (role, content)
        VALUES (?, ?)
        """,
        (role, content)
    )

    conexao.commit()
    conexao.close()


def carregar_historico(limite=10):
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute(
        """
        SELECT role, content
        FROM conversas
        ORDER BY id DESC
        LIMIT ?
        """,
        (limite,)
    )

    resultados = cursor.fetchall()
    conexao.close()

    resultados.reverse()

    return [
        {
            "role": role,
            "content": content
        }
        for role, content in resultados
    ]