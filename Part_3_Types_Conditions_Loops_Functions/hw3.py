#!/usr/bin/env python

UNKNOWN_COMMAND_MSG = "Unknown command!"
NONPOSITIVE_VALUE_MSG = "Value must be grater than zero!"
INCORRECT_DATE_MSG = "Invalid date!"
NOT_EXISTS_CATEGORY = "Category not exists!"
OP_SUCCESS_MSG = "Added"

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

EXPENSE_CATEGORIES = {
    "Food": ("Supermarket", "Restaurants", "FastFood", "Coffee", "Delivery"),
    "Transport": ("Taxi", "Public transport", "Gas", "Car service"),
    "Housing": ("Rent", "Utilities", "Repairs", "Furniture"),
    "Health": ("Pharmacy", "Doctors", "Dentist", "Lab tests"),
    "Entertainment": ("Movies", "Concerts", "Games", "Subscriptions"),
    "Clothing": ("Outerwear", "Casual", "Shoes", "Accessories"),
    "Education": ("Courses", "Books", "Tutors"),
    "Communications": ("Mobile", "Internet", "Subscriptions"),
}


def is_leap_year(year: int) -> bool:
    """
    Для заданного года определяет: високосный (True) или невисокосный (False).
    :param int year: Проверяемый год
    :return: Значение високосности.
    :return: True, если 366, иначе False.
    :rtype: bool
    """
    if year % 4 != 0:
        return False
    if year % 100 != 0:
        return True
    return year % 400 == 0


def is_correct_day(day: int, month: int, year: int) -> bool:
    if month < 1 or month > MONTH_IN_YEAR or day < 1:
        return False

    if month in THIRTY_DAY_MONTHS:
        return day <= DAY_THIRTY

    if month == INDEX_FEBRUARY:
        return day <= DAY_FEBRUARY + int(is_leap_year(year))

    return day <= DAY_THIRTY_ONE


def extract_date(maybe_dt: str) -> Date | None:
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

    if maybe_amount.startswith("-"):
        return None

    maybe_amount = maybe_amount.replace(",", ".")
    if maybe_amount.count(".") > 1:
        return None

    if maybe_amount[0] == "+":
        maybe_amount = maybe_amount[1:]

    if not maybe_amount:
        return None

    for char in maybe_amount:
        if char != "." and not char.isdigit():
            return None

    amount = float(maybe_amount)
    return amount if amount > 0 else None


def format_detail_amount(value: float) -> str:
    if value.is_integer():
        return str(int(value))
    formatted = f"{value:.2f}"
    if formatted.endswith(".00"):
        return formatted[:-3]
    return formatted


def is_earlier(first_date: Date, second_date: Date) -> bool:
    return (first_date[2], first_date[1], first_date[0]) <= (
        second_date[2],
        second_date[1],
        second_date[0],
    )


def is_same_month(first_date: Date, second_date: Date) -> bool:
    return first_date[1] == second_date[1] and first_date[2] == second_date[2]


def collect_income_stats(date: Date, incomes: list[Income]) -> tuple[
    float, float]:
    total_income: float = 0
    month_income: float = 0

    for amount, income_date in incomes:
        if is_earlier(income_date, date):
            total_income += amount
            if is_same_month(income_date, date):
                month_income += amount

    return total_income, month_income


def collect_cost_stats(
    date: Date,
    costs: list[Cost],
) -> tuple[float, float, dict[str, float]]:
    total_cost: float = 0
    month_cost: float = 0
    category_cost: dict[str, float] = {}

    for category, amount, cost_date in costs:
        if is_earlier(cost_date, date):
            total_cost += amount
            if is_same_month(cost_date, date):
                month_cost += amount
                category_cost[category] = category_cost.get(category,
                                                            0) + amount

    return total_cost, month_cost, category_cost


def print_delta(month_income: float, month_cost: float) -> None:
    delta = month_income - month_cost
    if delta >= 0:
        print(f"This month, the profit amounted to {delta:.2f} rubles.")
    else:
        print(f"This month, the loss amounted to {abs(delta):.2f} rubles.")


def print_category_stats(category_cost: dict[str, float]) -> None:
    print()
    print("Details (category: amount):")
    if not category_cost:
        return

    for idx, (category, amount) in enumerate(sorted(category_cost.items()), 1):
        formatted_amount = format_detail_amount(amount)
        print(f"{idx}. {category}: {formatted_amount}")


def print_date_stats(date: Date, total_capital: float, month_income: float,
    month_cost: float, category_cost: dict[str, float]) -> None:
    day, month, year = date
    print(f"Your statistics as of {day:02d}-{month:02d}-{year:04d}:")
    print(f"Total capital: {total_capital:.2f} rubles")
    print_delta(month_income, month_cost)
    print(f"Income: {month_income:.2f} rubles")
    print(f"Expenses: {month_cost:.2f} rubles")
    print_category_stats(category_cost)


def print_stats(date: Date, incomes: list[Income], costs: list[Cost]) -> None:
    total_income, month_income = collect_income_stats(date, incomes)
    total_cost, month_cost, category_cost = collect_cost_stats(date, costs)
    total_capital = total_income - total_cost

    print_date_stats(date, total_capital, month_income, month_cost,
                     category_cost)


def find_error_income(details: list[str]) -> tuple[
    bool, float | None, Date | None]:
    if len(details) != LEN_INCOME:
        print(UNKNOWN_COMMAND_MSG)
        return True, None, None

    amount = extract_amount(details[1])
    if amount is None:
        print(NONPOSITIVE_VALUE_MSG)
        return True, None, None

    date = extract_date(details[2])
    if date is None:
        print(INCORRECT_DATE_MSG)
        return True, amount, None

    return False, amount, date


def find_error_cost(details: list[str]) -> tuple[
    bool, str | None, float | None, Date | None]:
    if len(details) != LEN_COST:
        print(UNKNOWN_COMMAND_MSG)
        return True, None, None, None

    if details[1] == "categories":
        return True, None, None, None

    category_name = details[1]
    if "::" not in category_name:
        print(NOT_EXISTS_CATEGORY)
        return True, None, None, None

    common_cat, specific_cat = category_name.split("::", 1)

    if common_cat not in EXPENSE_CATEGORIES or specific_cat not in \
        EXPENSE_CATEGORIES[common_cat]:
        print(NOT_EXISTS_CATEGORY)
        print("Available categories:")
        for common, specifics in EXPENSE_CATEGORIES.items():
            for specific in specifics:
                print(f"{common}::{specific}")
        return True, None, None, None

    amount = extract_amount(details[2])
    if amount is None:
        print(NONPOSITIVE_VALUE_MSG)
        return True, category_name, None, None

    date = extract_date(details[3])
    if date is None:
        print(INCORRECT_DATE_MSG)
        return True, category_name, amount, None

    return False, category_name, amount, date


def handle_income(details: list[str], incomes: list[Income]) -> None:
    has_error, amount, date = find_error_income(details)
    if has_error or amount is None or date is None:
        return

    incomes.append((amount, date))
    print(OP_SUCCESS_MSG)


def handle_cost(details: list[str], costs: list[Cost]) -> None:
    if len(details) == 2 and details[1] == "categories":
        for common, specifics in EXPENSE_CATEGORIES.items():
            for specific in specifics:
                print(f"{common}::{specific}")
        return

    has_error, category_name, amount, date = find_error_cost(details)
    if has_error or category_name is None or amount is None or date is None:
        return

    costs.append((category_name, amount, date))
    print(OP_SUCCESS_MSG)


def handle_stats(details: list[str], incomes: list[Income],
    costs: list[Cost]) -> None:
    if len(details) != 2:  # stats <date>
        print(UNKNOWN_COMMAND_MSG)
        return

    date = extract_date(details[1])
    if date is None:
        print(INCORRECT_DATE_MSG)
        return

    print_stats(date, incomes, costs)


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
        handle_stats(details, incomes, costs)
    else:
        print(UNKNOWN_COMMAND_MSG)


def main() -> None:
    incomes: list[Income] = []
    costs: list[Cost] = []

    while True:
        try:
            line = input()
            if not line:
                break

            details = line.split()
            if not details:
                print(UNKNOWN_COMMAND_MSG)
                continue

            if details[0] not in COMMAND:
                print(UNKNOWN_COMMAND_MSG)
                continue

            process_command(details, incomes, costs)
        except EOFError:
            break


if __name__ == "__main__":
    main()