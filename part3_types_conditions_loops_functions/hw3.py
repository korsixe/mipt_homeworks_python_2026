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
    "Other": ("SomeCategory", "SomeOtherCategory"),
}

THIRTY_DAY_MONTHS = (4, 6, 9, 11)
COMMAND = ("income", "cost", "stats")
LEN_DATE = 3
LEN_INCOME = 3
LEN_STATS = 2
LEN_COST_CATEGORIES = 2
LEN_COST = 4
MONTH_IN_YEAR = 12
INDEX_FEBRUARY = 2
DAY_FEBRUARY = 28
DAY_THIRTY = 30
DAY_THIRTY_ONE = 31

type Date = tuple[int, int, int]
type Income = tuple[float, Date]
type Cost = tuple[str, float, Date]
type TransactionValue = str | float | Date | None
type Transaction = dict[str, TransactionValue]
type IncomeStats = tuple[float, float]
type CostStats = tuple[float, float, dict[str, float]]

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
        if is_leap_year(year):
            return day <= DAY_FEBRUARY + 1
        return day <= DAY_FEBRUARY

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


def prepare_amount(maybe_amount: str) -> tuple[int, str] | None:
    if not maybe_amount:
        return None

    normalized = maybe_amount.replace(",", ".")

    sign = 1
    if normalized[0] in "+-":
        sign = -1 if normalized[0] == "-" else 1
        normalized = normalized[1:]

    if not normalized:
        return None

    return sign, normalized


def is_valid_amount_body(maybe_amount: str) -> bool:
    if maybe_amount.count(".") > 1:
        return False

    has_digit = False
    for char in maybe_amount:
        if char == ".":
            continue
        if not char.isdigit():
            return False
        has_digit = True

    return has_digit


def extract_amount(maybe_amount: str) -> float | None:
    prepared_amount = prepare_amount(maybe_amount)
    if prepared_amount is None:
        return None

    sign, normalized = prepared_amount
    if not is_valid_amount_body(normalized):
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

    financial_transactions_storage.append({"category": category_name, "amount": amount, "date": parsed_date})
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


def append_transaction(
    transaction: Transaction,
    incomes: list[Income],
    costs: list[Cost],
) -> None:
    amount_value = transaction.get("amount")
    transaction_date = transaction.get("date")
    if not isinstance(transaction_date, tuple):
        return

    if not isinstance(amount_value, (int, float)):
        return

    amount: float = float(amount_value)
    category_value = transaction.get("category")

    if isinstance(category_value, str):
        costs.append((category_value, amount, transaction_date))
    else:
        incomes.append((amount, transaction_date))


def collect_income_stats(date: Date, incomes: list[Income]) -> IncomeStats:
    total_capital: float = 0
    month_income: float = 0

    for amount, income_date in incomes:
        if is_earlier(income_date, date):
            total_capital += amount
            if is_same_month(income_date, date):
                month_income += amount

    return total_capital, month_income


def collect_cost_stats(date: Date, costs: list[Cost]) -> CostStats:
    total_cost: float = 0
    month_cost: float = 0
    category_cost: dict[str, float] = {}

    for category, amount, cost_date in costs:
        if is_earlier(cost_date, date):
            total_cost += amount
            if is_same_month(cost_date, date):
                month_cost += amount
                category_cost.setdefault(category, float(0))
                category_cost[category] += amount

    return total_cost, month_cost, category_cost


def build_delta_line(month_income: float, month_cost: float) -> str:
    delta = month_income - month_cost
    delta_type = "profit"
    delta_value = delta

    if delta < 0:
        delta_type = "loss"
        delta_value = -delta

    return f"In this month the {delta_type} was {delta_value:.2f} рублей"


def build_title_line(date: Date) -> str:
    return f"Your statistics on {normalize_date(date)}:"


def build_total_capital_line(
    income_stats: tuple[float, float],
    cost_stats: tuple[float, float, dict[str, float]],
) -> str:
    total_capital = income_stats[0] - cost_stats[0]
    return f"Total capital: {total_capital:.2f} рублей"


def build_income_line(month_income: float) -> str:
    return f"Income: {month_income:.2f} рублей"


def build_cost_line(month_cost: float) -> str:
    return f"Cost: {month_cost:.2f} рублей"


def collect_stats(date: Date) -> tuple[IncomeStats, CostStats]:
    incomes: list[Income] = []
    costs: list[Cost] = []
    for transaction in financial_transactions_storage:
        append_transaction(transaction, incomes, costs)
    return collect_income_stats(date, incomes), collect_cost_stats(date, costs)


def add_category_lines(lines: list[str], category_cost: dict[str, float]) -> None:
    sorted_items = sorted(category_cost.items())
    for idx, (cat, cost) in enumerate(sorted_items, start=1):
        lines.append(f"{idx}. {cat}: {format_detail_amount(cost)}")

def build_stats_lines(
    date: Date,
    income_stats: IncomeStats,
    cost_stats: CostStats,
) -> list[str]:
    lines = [
        build_title_line(date),
        build_total_capital_line(income_stats, cost_stats),
        build_delta_line(income_stats[1], cost_stats[1]),
        build_income_line(income_stats[1]),
        build_cost_line(cost_stats[1]),
        "",
        "Details (category: sum):",
    ]
    add_category_lines(lines, cost_stats[2])
    return lines


def stats_handler(report_date: str) -> str:
    date = extract_date(report_date)
    if date is None:
        return INCORRECT_DATE_MSG

    income_stats, cost_stats = collect_stats(date)
    return "\n".join(build_stats_lines(date, income_stats, cost_stats))


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


def handle_income(details: list[str]) -> None:
    if find_erorr_income(details):
        return

    amount = extract_amount(details[1])
    date = extract_date(details[2])
    if amount is None or date is None:
        return

    print(income_handler(amount, details[2]))


def handle_cost(details: list[str]) -> None:
    if len(details) == LEN_COST_CATEGORIES and details[1] == "categories":
        print(cost_categories_handler())
        return

    if find_error_cost(details):
        return
    category_name = details[1]
    amount = extract_amount(details[2])
    date = extract_date(details[3])
    if amount is None or date is None:
        return

    print(cost_handler(category_name, amount, normalize_date(date)))


def handle_stats(details: list[str]) -> None:
    if len(details) != LEN_STATS:
        print(UNKNOWN_COMMAND_MSG)
        return

    date = extract_date(details[1])
    if date is None:
        print(INCORRECT_DATE_MSG)
        return

    print(stats_handler(normalize_date(date)))


def process_command(details: list[str]) -> None:
    command = details[0]

    if command == "income":
        handle_income(details)
    elif command == "cost":
        handle_cost(details)
    elif command == "stats":
        handle_stats(details)
    else:
        print(UNKNOWN_COMMAND_MSG)


def main() -> None:
    while True:
        line = input()
        if not line:
            break
        details = line.split()
        if not details or details[0] not in COMMAND:
            print(UNKNOWN_COMMAND_MSG)
            continue

        process_command(details)


if __name__ == "__main__":
    main()
