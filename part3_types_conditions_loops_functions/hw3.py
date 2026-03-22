#!/usr/bin/env python

UNKNOWN_COMMAND_MSG = "Unknown command!"
NONPOSITIVE_VALUE_MSG = "Value must be grater than zero!"
INCORRECT_DATE_MSG = "Invalid date!"
NOT_EXISTS_CATEGORY = "Category not exists!"
OP_SUCCESS_MSG = "Added"

EXPENSE_CATEGORIES = {
    "Food": ("Supermarket", "Restaurants", "FastFood", "Coffee", "Delivery"),
    "Transport": ("Taxi", "Public transport", "Gas", "Car service"),
    "Housing": ("Rent", "Utilities", "Repairs", "Furniture"),
    "Health": ("Pharmacy", "Doctors", "Dentist", "Lab tests"),
    "Entertainment": ("Movies", "Concerts", "Games", "Subscriptions"),
    "Clothing": ("Outerwear", "Casual", "Shoes", "Accessories"),
    "Education": ("Courses", "Books", "Tutors"),
    "Communications": ("Mobile", "Internet", "Subscriptions"),
    "Other": ("Other",),
}

THIRTY_DAY_MONTHS = (4, 6, 9, 11)
COMMAND = ("income", "cost", "stats")
LEN_DATE = 3
LEN_INCOME = 3
LEN_COST = 4
MONTH_IN_YEAR = 12
INDEX_FEBRUARY = 2
DAY_FEBRUARY = 28
DAY_THIRTY = 30
DAY_THIRTY_ONE = 31

Date = tuple[int, int, int]
Income = tuple[float, Date]
Cost = tuple[str, float, Date]
TransactionValue = str | float | Date | None
Transaction = dict[str, TransactionValue]

financial_transactions_storage: list[Transaction] = []


def is_leap_year(year: int) -> bool:
    """
    Для заданного года определяет: високосный (True) или невисокосный (False).

    :param int year: Проверяемый год
    :return: Значение високосности.
    :rtype: bool
    """
    if year % 4 != 0:
        return False
    if year % 100 != 0:
        return True
    return year % 400 == 0


def is_invalid_category(maybe_category: str) -> bool:
    if "::" not in maybe_category:
        return True

    common_cat, specific_cat = maybe_category.split("::", 1)
    if common_cat not in EXPENSE_CATEGORIES:
        return True

    return specific_cat not in EXPENSE_CATEGORIES[common_cat]


def is_correct_day(day: int, month: int, year: int) -> bool:
    if month < 1 or month > MONTH_IN_YEAR or day < 1:
        return False

    if month in THIRTY_DAY_MONTHS:
        return day <= DAY_THIRTY

    if month == INDEX_FEBRUARY:
        return day <= DAY_FEBRUARY + int(is_leap_year(year))

    return day <= DAY_THIRTY_ONE


def extract_date(maybe_dt: str) -> tuple[int, int, int] | None:
    """
    Парсит дату формата DD-MM-YYYY из строки.

    :param str maybe_dt: Проверяемая строка
    :return: tuple формата (день, месяц, год) или None, если дата неправильная.
    :rtype: tuple[int, int, int] | None
    """
    parts = maybe_dt.split("-")
    if len(parts) != LEN_DATE:
        return None

    if not all(part.isdigit() for part in parts):
        return None

    day = int(parts[0])
    month = int(parts[1])
    year = int(parts[2])

    if is_correct_day(day, month, year):
        return day, month, year
    return None


def extract_amount(maybe_amount: str) -> float | None:
    if not maybe_amount:
        return None

    normalized = maybe_amount.replace(",", ".")
    if normalized.count(".") > 1:
        return None

    sign = -1 if normalized[0] == "-" else 1
    if normalized[0] in "+-":
        normalized = normalized[1:]

    if not normalized or not any(char.isdigit() for char in normalized):
        return None

    if any(not (char.isdigit() or char == ".") for char in normalized):
        return None

    return sign * float(normalized)


def normalize_date(date: Date) -> str:
    day, month, year = date
    return f"{day:02d}-{month:02d}-{year:04d}"


def save_invalid_transaction() -> None:
    financial_transactions_storage.append({})


def income_handler(amount: float, income_date: str) -> str:
    parsed_date = extract_date(income_date)

    if amount <= 0:
        save_invalid_transaction()
        return NONPOSITIVE_VALUE_MSG

    if parsed_date is None:
        save_invalid_transaction()
        return INCORRECT_DATE_MSG

    financial_transactions_storage.append({"amount": amount, "date": parsed_date})
    return OP_SUCCESS_MSG


def cost_handler(category_name: str, amount: float, income_date: str) -> str:
    parsed_date = extract_date(income_date)

    if is_invalid_category(category_name):
        save_invalid_transaction()
        return NOT_EXISTS_CATEGORY

    if amount <= 0:
        save_invalid_transaction()
        return NONPOSITIVE_VALUE_MSG

    if parsed_date is None:
        save_invalid_transaction()
        return INCORRECT_DATE_MSG

    financial_transactions_storage.append(
        {"category": category_name, "amount": amount, "date": parsed_date}
    )
    return OP_SUCCESS_MSG


def cost_categories_handler() -> str:
    result: list[str] = []
    for common_cat, subcategories in EXPENSE_CATEGORIES.items():
        result.extend(f"{common_cat}::{subcategory}" for subcategory in subcategories)
    return "\n".join(result)


def format_detail_amount(value: float) -> str:
    result = f"{value:.10f}".rstrip("0").rstrip(".")
    return result or "0"


def is_earlier(first_date: Date, second_date: Date) -> bool:
    return (first_date[2], first_date[1], first_date[0]) <= (
        second_date[2],
        second_date[1],
        second_date[0],
    )


def is_same_month(first_date: Date, second_date: Date) -> bool:
    if first_date[1] != second_date[1]:
        return False
    return first_date[2] == second_date[2]


def extract_transaction_date(transaction: Transaction) -> Date | None:
    raw_date = transaction.get("date")
    if isinstance(raw_date, tuple):
        return raw_date
    if isinstance(raw_date, str):
        return extract_date(raw_date)
    return None


def append_transaction(
    transaction: Transaction,
    incomes: list[Income],
    costs: list[Cost],
) -> None:
    amount_value = transaction.get("amount")
    transaction_date = extract_transaction_date(transaction)
    if not isinstance(amount_value, (int, float)) or transaction_date is None:
        return

    amount = float(amount_value)
    category_value = transaction.get("category")
    if isinstance(category_value, str):
        costs.append((category_value, amount, transaction_date))
        return

    incomes.append((amount, transaction_date))


def split_storage() -> tuple[list[Income], list[Cost]]:
    incomes: list[Income] = []
    costs: list[Cost] = []

    for transaction in financial_transactions_storage:
        append_transaction(transaction, incomes, costs)

    return incomes, costs


def collect_income_stats(date: Date, incomes: list[Income]) -> tuple[float, float]:
    total_capital: float = 0
    month_income: float = 0

    for amount, income_date in incomes:
        if is_earlier(income_date, date):
            total_capital += amount
            if is_same_month(income_date, date):
                month_income += amount

    return total_capital, month_income


def collect_cost_stats(
    date: Date,
    costs: list[Cost],
) -> tuple[float, float, dict[str, float]]:
    total_cost: float = 0
    month_cost: float = 0
    category_cost: dict[str, float] = {}

    for category_name, amount, cost_date in costs:
        if is_earlier(cost_date, date):
            total_cost += amount
            if is_same_month(cost_date, date):
                month_cost += amount
                category_cost.setdefault(category_name, 0.0)
                category_cost[category_name] += amount

    return total_cost, month_cost, category_cost


def build_delta_line(month_income: float, month_cost: float) -> str:
    delta = month_income - month_cost
    result_word = "profit" if delta >= 0 else "loss"
    result_amount = delta if delta >= 0 else -delta
    return f"In this month the {result_word} was {result_amount:.2f} рублей"


def print_delta(month_income: float, month_cost: float) -> None:
    print(build_delta_line(month_income, month_cost))


def print_category_stats(category_cost: dict[str, float]) -> None:
    print()
    print("Details (category: sum):")
    for idx, (category, amount) in enumerate(sorted(category_cost.items()), start=1):
        print(f"{idx}. {category}: {format_detail_amount(amount)}")


def print_date(date: Date) -> None:
    print(f"Your statistics on {normalize_date(date)}:")


def print_stats(date: Date) -> None:
    print(stats_handler(normalize_date(date)))


def build_stats_summary(date: Date) -> tuple[float, float, float, dict[str, float]]:
    incomes, costs = split_storage()
    total_income, month_income = collect_income_stats(date, incomes)
    total_cost, month_cost, category_cost = collect_cost_stats(date, costs)
    return total_income - total_cost, month_income, month_cost, category_cost


def add_category_lines(lines: list[str], category_cost: dict[str, float]) -> None:
    for idx, (category, amount) in enumerate(sorted(category_cost.items()), start=1):
        lines.append(f"{idx}. {category}: {format_detail_amount(amount)}")


def build_stats_lines(
    date: Date,
    total_capital: float,
    month_income: float,
    month_cost: float,
    category_cost: dict[str, float],
) -> list[str]:
    lines = [
        f"Your statistics on {normalize_date(date)}:",
        f"Total capital: {total_capital:.2f} рублей",
        build_delta_line(month_income, month_cost),
        f"Income: {month_income:.2f} рублей",
        f"Cost: {month_cost:.2f} рублей",
        "",
        "Details (category: sum):",
    ]
    add_category_lines(lines, category_cost)
    return lines


def stats_handler(report_date: str) -> str:
    date = extract_date(report_date)
    if date is None:
        return INCORRECT_DATE_MSG

    total_capital, month_income, month_cost, category_cost = build_stats_summary(date)
    return "\n".join(
        build_stats_lines(date, total_capital, month_income, month_cost, category_cost)
    )


def find_erorr_income(details: list[str]) -> bool:
    if len(details) != LEN_INCOME:
        print(UNKNOWN_COMMAND_MSG)
        return True

    amount = extract_amount(details[1])
    if amount is None or amount <= 0:
        print(NONPOSITIVE_VALUE_MSG)
        return True

    date = extract_date(details[2])
    if date is None:
        print(INCORRECT_DATE_MSG)
        return True

    return False


def find_error_cost(details: list[str]) -> bool:
    if len(details) != LEN_COST:
        print(UNKNOWN_COMMAND_MSG)
        return True

    category_name = details[1]
    if is_invalid_category(category_name):
        print(NOT_EXISTS_CATEGORY)
        print(cost_categories_handler())
        return True

    amount = extract_amount(details[2])
    if amount is None or amount <= 0:
        print(NONPOSITIVE_VALUE_MSG)
        return True

    date = extract_date(details[3])
    if date is None:
        print(INCORRECT_DATE_MSG)
        return True

    return False


def handle_income(details: list[str], incomes: list[Income]) -> None:
    if find_erorr_income(details):
        return

    amount = extract_amount(details[1])
    date = extract_date(details[2])
    if amount is None or date is None:
        return

    incomes.append((amount, date))
    print(income_handler(amount, normalize_date(date)))


def handle_cost(details: list[str], costs: list[Cost]) -> None:
    if find_error_cost(details):
        return

    category_name = details[1]
    amount = extract_amount(details[2])
    date = extract_date(details[3])
    if amount is None or date is None:
        return

    costs.append((category_name, amount, date))
    print(cost_handler(category_name, amount, normalize_date(date)))


def handle_stats(details: list[str]) -> None:
    if len(details) != LEN_INCOME - 1:
        print(UNKNOWN_COMMAND_MSG)
        return

    date = extract_date(details[1])
    if date is None:
        print(INCORRECT_DATE_MSG)
        return

    print(stats_handler(normalize_date(date)))


def process_command(
    details: list[str],
    incomes: list[Income],
    costs: list[Cost],
) -> None:
    command = details[0]

    if command == "income":
        handle_income(details, incomes)
    elif command == "cost":
        handle_cost(details, costs)
    elif command == "stats":
        handle_stats(details)
    else:
        print(UNKNOWN_COMMAND_MSG)
[22.03.2026 13:11] Андрей: def main() -> None:
    incomes: list[Income] = []
    costs: list[Cost] = []

    while True:
        line = input()
        if not line:
            break
        details = line.split()
        if not details or details[0] not in COMMAND:
            print(UNKNOWN_COMMAND_MSG)
            continue

        process_command(details, incomes, costs)


if __name__ == "__main__":
    main()
