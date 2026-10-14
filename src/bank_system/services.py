from bank_system.models import Account, CurrentAccount, SavingsAccount, Customer
from bank_system.value_objects import Money, Transaction
from bank_system.protocols import Notifier
from bank_system.repositories import InMemoryRepository


class ConsoleNotifier:
    def send(self, recipient: str, message: str) -> None:
        print(f"[Сповіщення на {recipient}]: {message}")


class BankService:
    """Сервіс для управління банківськими рахунками за принципами SOLID та DI."""

    def __init__(
        self,
        account_repository: InMemoryRepository[Account],
        transaction_repository: InMemoryRepository[Transaction],
        notifier: Notifier,
    ) -> None:
        self._accounts = account_repository
        self._transactions = transaction_repository
        self._notifier = notifier

    def create_account(
        self,
        account_number: str,
        customer: Customer,
        initial_amount: float = 0.0,
        currency: str = "UAH",
        account_type: str = "current",
    ) -> Account:
        """Створення нового рахунку з перевіркою на існування та початковий баланс."""
        if self.find_account_by_number(account_number) is not None:
            raise ValueError(f"Рахунок з номером '{account_number}' вже існує.")
        if initial_amount < 0:
            raise ValueError("Початковий баланс не може бути від'ємним.")

        money = Money(initial_amount, currency)
        account: Account  # Явна типізація базовим класом
        if account_type == "savings":
            account = SavingsAccount(account_number, customer, money)
        else:
            account = CurrentAccount(account_number, customer, money)

        self._accounts.add(account)
        self._notifier.send(customer.email, f"Рахунок {account_number} успішно відкрито!")
        return account

    def find_account_by_number(self, account_number: str) -> Account | None:
        """Пошук рахунку за точним номером у репозиторії."""
        for account in self._accounts.all():
            if account.account_number == account_number:
                return account
        return None

    def search_accounts_by_owner(self, owner_name: str) -> list[Account]:
        """Пошук рахунків за ім'ям власника (підстрока)."""
        query = owner_name.strip().lower()
        return [
            acc for acc in self._accounts.all()
            if query in acc.customer.name.lower()
        ]

    def get_total_funds(self) -> float:
        """Обчислення загальної суми коштів на всіх рахунках."""
        total: float = sum(account.balance.amount for account in self._accounts.all())
        return total

    def deposit(self, account_number: str, amount: float, currency: str = "UAH") -> None:
        """Поповнення рахунку з фіксацією транзакції."""
        account = self.find_account_by_number(account_number)
        if account is None:
            raise ValueError(f"Рахунок {account_number} не знайдено")
        
        money = Money(amount, currency)
        account.deposit(money)

        tx = Transaction(
            id=len(self._transactions.all()) + 1,
            account_number=account_number,
            amount=money,
            transaction_type="deposit"
        )
        self._transactions.add(tx)
        self._notifier.send(account.customer.email, f"Поповнення рахунку на суму {money}")

    def withdraw(self, account_number: str, amount: float, currency: str = "UAH") -> None:
        """Зняття коштів з рахунку з перевіркою обмежень."""
        account = self.find_account_by_number(account_number)
        if account is None:
            raise ValueError(f"Рахунок {account_number} не знайдено")

        money = Money(amount, currency)
        account.withdraw(money)

        tx = Transaction(
            id=len(self._transactions.all()) + 1,
            account_number=account_number,
            amount=money,
            transaction_type="withdraw"
        )
        self._transactions.add(tx)
        self._notifier.send(account.customer.email, f"Зняття коштів: {money}")