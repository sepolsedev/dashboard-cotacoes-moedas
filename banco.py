"""Carga e leitura: armazenamento local em SQLite."""
from pathlib import Path
import sqlite3

# O banco fica junto ao código, independentemente da pasta do terminal.
CAMINHO_BANCO = Path(__file__).resolve().parent / "cotacoes.db"


def criar_tabela():
    with sqlite3.connect(CAMINHO_BANCO) as conexao:
        conexao.execute("""
            CREATE TABLE IF NOT EXISTS cotacoes (
                moeda TEXT NOT NULL,
                data TEXT NOT NULL,
                compra REAL NOT NULL CHECK(compra > 0),
                venda REAL NOT NULL CHECK(venda > 0),
                instante INTEGER NOT NULL,
                PRIMARY KEY (moeda, data)
            )
        """)


def salvar_cotacoes(registros):
    """Atualiza o mesmo dia sem duplicar e sem substituir por dados mais antigos."""
    with sqlite3.connect(CAMINHO_BANCO) as conexao:
        conexao.executemany("""
            INSERT INTO cotacoes (moeda, data, compra, venda, instante)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(moeda, data) DO UPDATE SET
                compra=excluded.compra, venda=excluded.venda,
                instante=excluded.instante
            WHERE excluded.instante >= cotacoes.instante
        """, registros)


def ler_cotacoes():
    import pandas as pd
    with sqlite3.connect(CAMINHO_BANCO) as conexao:
        return pd.read_sql_query(
            "SELECT moeda, data, compra, venda FROM cotacoes ORDER BY data, moeda",
            conexao,
        )
