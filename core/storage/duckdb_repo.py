from __future__ import annotations
from collections import defaultdict
from datetime import date
from pathlib import Path

import duckdb

from core.models import Account, Snapshot, NetWorthPoint, AccountType, Source
from core.storage.base import Repository

_SCHEMA = """
CREATE SEQUENCE IF NOT EXISTS seq_account_id START 1;
CREATE TABLE IF NOT EXISTS accounts (
    id INTEGER PRIMARY KEY DEFAULT nextval('seq_account_id'),
    name VARCHAR UNIQUE NOT NULL,
    type VARCHAR NOT NULL,
    currency VARCHAR NOT NULL DEFAULT 'EUR'
);
 
CREATE SEQUENCE IF NOT EXISTS seq_snapshot_id START 1;
CREATE TABLE IF NOT EXISTS snapshots (
    id INTEGER PRIMARY KEY DEFAULT nextval('seq_snapshot_id'),
    account_id INTEGER NOT NULL REFERENCES accounts(id),
    value DOUBLE NOT NULL,
    as_of DATE NOT NULL,
    source VARCHAR NOT NULL DEFAULT 'manual',
    UNIQUE (account_id, as_of)
);
"""


class DuckDBRepository(Repository):
    def __init__(
        self, db_path: str | Path = "/workspaces/life-tracker/data/lifetracker.duckdb"
    ):
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._con = duckdb.connect(str(db_path))
        self._con.execute(_SCHEMA)

    def close(self) -> None:
        self._con.close()

    def __enter__(self) -> "DuckDBRepository":
        return self

    def __exit__(self, *exc) -> None:
        self.close()

    # accounts

    def add_account(self, account: Account) -> Account:
        row = self._con.execute(
            """
            INSERT INTO accounts (name, type, currency)
            VALUES (?, ?, ?)
            ON CONFLICT (name) DO UPDATE SET type = excluded.type, currency = excluded.currency
            RETURNING id, name, type, currency
            """,
            [account.name, account.type.value, account.currency],
        ).fetchone()
        return Account(
            id=row[0], name=row[1], type=AccountType(row[2]), currency=row[3]
        )

    def get_accounts(self, type_: AccountType | None = None) -> list[Account]:
        query = "SELECT id, name, type, currency FROM accounts"
        params = []
        if type_ is not None:
            query += " WHERE type = ?"
            params.append(type_.value)
        rows = self._con.execute(query, params).fetchall()
        return [
            Account(id=row[0], name=row[1], type=AccountType(row[2]), currency=row[3])
            for row in rows
        ]

    def log_snapshot(self, snapshot: Snapshot) -> Snapshot:
        row = self._con.execute(
            """
            INSERT INTO snapshots (account_id, value, as_of, source)
            VALUES (?, ?, ?, ?)
            ON CONFLICT (account_id, as_of) DO UPDATE SET value = excluded.value, source = excluded.source
            RETURNING id, account_id, value, as_of, source
            """,
            [
                snapshot.account_id,
                snapshot.value,
                snapshot.as_of,
                snapshot.source.value,
            ],
        ).fetchone()
        return Snapshot(
            id=row[0],
            account_id=row[1],
            value=row[2],
            as_of=row[3],
            source=Source(row[4]),
        )

    def get_snapshots(
        self,
        account_id: int | None = None,
        start: date | None = None,
        end: date | None = None,
    ) -> list[Snapshot]:
        clauses, params = [], []
        if account_id is not None:
            clauses.append("account_id = ?")
            params.append(account_id)
        if start is not None:
            clauses.append("as_of >= ?")
            params.append(start)
        if end is not None:
            clauses.append("as_of <= ?")
            params.append(end)
        where_clause = f"WHERE {' AND '.join(clauses)}" if clauses else ""
        rows = self._con.execute(
            f"SELECT id, account_id, value, as_of, source FROM snapshots {where_clause} ORDER BY as_of",
            params,
        ).fetchall()
        return [
            Snapshot(
                id=row[0],
                account_id=row[1],
                value=row[2],
                as_of=row[3],
                source=Source(row[4]),
            )
            for row in rows
        ]

    def latest_snapshot(self, account_id: int) -> Snapshot | None:
        row = self._con.execute(
            """
            SELECT id, account_id, value, as_of, source
            FROM snapshots
            WHERE account_id = ?
            ORDER BY as_of DESC
            LIMIT 1
            """,
            [account_id],
        ).fetchone()
        if row is None:
            return None
        return Snapshot(
            id=row[0],
            account_id=row[1],
            value=row[2],
            as_of=row[3],
            source=Source(row[4]),
        )

    def net_worth_timeseries(self) -> list[NetWorthPoint]:
        rows = self._con.execute("""
            SELECT as_of, type, SUM(value)
            FROM snapshots
            JOIN accounts ON snapshots.account_id = accounts.id
            GROUP BY as_of, type
            ORDER BY as_of
            """).fetchall()
        by_date: dict[date, dict[str, float]] = defaultdict(dict)
        for as_of, type_, total in rows:
            by_date[as_of][type_] = total
        return [
            NetWorthPoint(
                as_of=d,
                cash=vals.get(AccountType.CASH.value, 0.0),
                stock=vals.get(AccountType.STOCK.value, 0.0),
                asset=vals.get(AccountType.ASSET.value, 0.0),
                debt=vals.get(AccountType.DEBT.value, 0.0),
            )
            for d, vals in sorted(by_date.items())
        ]
