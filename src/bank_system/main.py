from bank_system.models import Customer, Account
from bank_system.value_objects import Transaction
from bank_system.repositories import InMemoryRepository
from bank_system.services import BankService, ConsoleNotifier


def main() -> None:
    print("=== ЗАПУСК БАНКІВСЬКОЇ СИСТЕМИ (Варіант 4 - ЛР №4) ===")

    # Dependency Injection
    account_repo = InMemoryRepository[Account]()
    transaction_repo = InMemoryRepository[Transaction]()
    notifier = ConsoleNotifier()

    bank_service = BankService(
        account_repository=account_repo,
        transaction_repository=transaction_repo,
        notifier=notifier,
    )

    # Клієнти та рахунки
    c1 = Customer(id=1, name="Олександр Петренко", email="petrenko@example.com")
    c2 = Customer(id=2, name="Марія Коваль", email="koval@example.com")

    bank_service.create_account("UA1234567890", c1, 5000.0, "UAH", "current")
    bank_service.create_account("UA0987654321", c2, 15000.0, "UAH", "savings")

    print("\n--- Виконання операцій ---")
    bank_service.deposit("UA1234567890", 2500.0)
    bank_service.withdraw("UA1234567890", 1000.0)
    bank_service.withdraw("UA0987654321", 5000.0)

    print("\n--- Звітність ---")
    total = bank_service.get_total_funds()
    print(f"Загальна сума коштів у банку: {total:.2f} UAH")

    print("\nСписок усіх рахунків:")
    for acc in account_repo.all():
        print(acc)


if __name__ == "__main__":
    main()