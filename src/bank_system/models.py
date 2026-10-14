from abc import ABC, abstractmethod
from dataclasses import dataclass
from bank_system.value_objects import Money
from collections.abc import Iterator

class AccountCollection:
    """Власний клас колекції рахунків із підтримкою протоколу контейнерів."""
    def __init__(self, accounts: list[Account] | None = None) -> None:
        self._accounts: list[Account] = accounts if accounts is not None else []

    def add(self, account: Account) -> None:
        self._accounts.append(account)

    def __len__(self) -> int:
        return len(self._accounts)

    def __iter__(self) -> Iterator[Account]:
        return iter(self._accounts)

    def __getitem__(self, index: int) -> Account:
        return self._accounts[index]

    def __contains__(self, account_number: str) -> bool:
        return any(acc.account_number == account_number for acc in self._accounts)

    def __str__(self) -> str:
        return f"AccountCollection(total={len(self._accounts)})"

@dataclass
class Customer:
    id: int
    name: str
    email: str

    def __str__(self) -> str:
        return f"Клієнт: {self.name} ({self.email})"


# Сумісність зі старим кодом 3-ї лаби
@dataclass
class BankAccount:
    account_number: str
    owner_name: str
    balance: float = 0.0


class Account(ABC):
    def __init__(self, account_number: str, customer: Customer, initial_balance: Money) -> None:
        self._account_number = account_number
        self._customer = customer
        self._balance = initial_balance

    @property
    def account_number(self) -> str:
        return self._account_number

    @property
    def customer(self) -> Customer:
        return self._customer

    @property
    def balance(self) -> Money:
        return self._balance

    def deposit(self, amount: Money) -> None:
        if amount.currency != self._balance.currency:
            raise ValueError("Невідповідність валюти депозиту")
        self._balance = self._balance + amount

    @abstractmethod
    def withdraw(self, amount: Money) -> None:
        pass

    @property
    def id(self) -> int:
        return abs(hash(self._account_number)) % (10 ** 8)

    def __str__(self) -> str:
        return f"Рахунок {self._account_number} [Баланс: {self._balance}]"


class SavingsAccount(Account):
    def __init__(self, account_number: str, customer: Customer, initial_balance: Money, min_balance: float = 100.0) -> None:
        super().__init__(account_number, customer, initial_balance)
        self._min_balance = min_balance

    def withdraw(self, amount: Money) -> None:
        if amount.currency != self._balance.currency:
            raise ValueError("Невідповідність валюти")
        if (self._balance.amount - amount.amount) < self._min_balance:
            raise ValueError(f"Порушення ліміту ощадного рахунку. Мінімальний залишок: {self._min_balance}")
        self._balance = self._balance - amount


class CurrentAccount(Account):
    def withdraw(self, amount: Money) -> None:
        if amount.currency != self._balance.currency:
            raise ValueError("Невідповідність валюти")
        self._balance = self._balance - amount