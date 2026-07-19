# Account, Snapshot dataclasses
from __future__ import annotations
from enum import Enum
from dataclasses import dataclass, field

from datetime import date


class AccountType(str, Enum):
    CASH = "cash"
    STOCK = "stock"
    ASSET = "asset"
    DEBT = "debt"


class Source(str, Enum):
    MANUAL = "manual"
    MARKET = "market"


@dataclass(slots=True)
class Account:
    id: int | None
    name: str
    type: AccountType
    currency: str = "EUR"


@dataclass(slots=True)
class Snapshot:
    account_id: int
    value: float
    as_of: date
    source: Source = Source.MANUAL
    id: int | None = None


@dataclass(slots=True)
class NetWorthPoint:
    as_of: date
    cash: float = 0.0
    stock: float = 0.0
    asset: float = 0.0
    debt: float = 0.0

    @property
    def net_worth(self) -> float:
        return self.cash + self.stock + self.asset - self.debt
