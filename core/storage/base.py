# abstract Repository interface
from __future__ import annotations
from abc import ABC, abstractmethod
from datetime import date
from core.models import Account, Snapshot, NetWorthPoint, AccountType


class Repository(ABC):

    @abstractmethod
    def add_account(self, account: Account) -> Account:
        return NotImplemented

    @abstractmethod
    def get_accounts(self, type_: AccountType | None = None) -> list[Account]:
        return NotImplemented

    @abstractmethod
    def log_snapshot(self, snapshot: Snapshot) -> Snapshot:
        return NotImplemented

    @abstractmethod
    def get_snapshots(
        self,
        account_id: int | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> list[Snapshot]:
        return NotImplemented

    @abstractmethod
    def latest_snapshot(self, account_id: int) -> Snapshot | None:
        return NotImplemented

    @abstractmethod
    def net_worth_timeseries(self) -> list[NetWorthPoint]:
        return NotImplemented
