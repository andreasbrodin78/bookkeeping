from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


@dataclass
class Account:
    id: int
    number: str
    name: str
    type: str


class BookkeepingDB:
    def __init__(self, db_path: str | Path = "bookkeeping.db") -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self.init_schema()

    def init_schema(self) -> None:
        self.conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                number TEXT NOT NULL UNIQUE,
                name TEXT NOT NULL,
                type TEXT NOT NULL CHECK(type IN ('asset', 'liability', 'income', 'expense'))
            );

            CREATE TABLE IF NOT EXISTS vouchers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tx_date TEXT NOT NULL,
                description TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                voucher_id INTEGER NOT NULL,
                account_id INTEGER NOT NULL,
                debit REAL NOT NULL DEFAULT 0,
                credit REAL NOT NULL DEFAULT 0,
                FOREIGN KEY(voucher_id) REFERENCES vouchers(id),
                FOREIGN KEY(account_id) REFERENCES accounts(id)
            );
            """
        )
        self.conn.commit()

    def add_account(self, number: str, name: str, account_type: str) -> None:
        self.conn.execute(
            "INSERT INTO accounts(number, name, type) VALUES(?, ?, ?)",
            (number, name, account_type),
        )
        self.conn.commit()

    def list_accounts(self) -> list[Account]:
        rows = self.conn.execute(
            "SELECT id, number, name, type FROM accounts ORDER BY number"
        ).fetchall()
        return [Account(**dict(row)) for row in rows]

    def add_voucher(
        self,
        tx_date: str,
        description: str,
        debit_account_id: int,
        credit_account_id: int,
        amount: float,
    ) -> None:
        voucher_id = self.conn.execute(
            "INSERT INTO vouchers(tx_date, description) VALUES(?, ?)",
            (tx_date, description),
        ).lastrowid
        self.conn.executemany(
            "INSERT INTO entries(voucher_id, account_id, debit, credit) VALUES(?, ?, ?, ?)",
            [
                (voucher_id, debit_account_id, amount, 0),
                (voucher_id, credit_account_id, 0, amount),
            ],
        )
        self.conn.commit()

    def summary(self) -> sqlite3.Row:
        row = self.conn.execute(
            """
            SELECT
                SUM(CASE WHEN a.type='asset' THEN e.debit - e.credit ELSE 0 END) AS assets,
                SUM(CASE WHEN a.type='liability' THEN e.credit - e.debit ELSE 0 END) AS liabilities,
                SUM(CASE WHEN a.type='income' THEN e.credit - e.debit ELSE 0 END) AS income,
                SUM(CASE WHEN a.type='expense' THEN e.debit - e.credit ELSE 0 END) AS expense
            FROM entries e
            JOIN accounts a ON a.id = e.account_id
            """
        ).fetchone()
        return row

    def recent_vouchers(self, limit: int = 20) -> Iterable[sqlite3.Row]:
        return self.conn.execute(
            """
            SELECT v.tx_date, v.description,
                   SUM(e.debit) AS total_debit,
                   SUM(e.credit) AS total_credit
            FROM vouchers v
            JOIN entries e ON e.voucher_id = v.id
            GROUP BY v.id, v.tx_date, v.description
            ORDER BY v.tx_date DESC, v.id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()

    def ledger(self) -> Iterable[sqlite3.Row]:
        return self.conn.execute(
            """
            SELECT a.number, a.name,
                   SUM(e.debit) AS debit,
                   SUM(e.credit) AS credit,
                   SUM(e.debit - e.credit) AS net
            FROM accounts a
            LEFT JOIN entries e ON e.account_id = a.id
            GROUP BY a.id, a.number, a.name
            ORDER BY a.number
            """
        ).fetchall()

    def close(self) -> None:
        self.conn.close()
