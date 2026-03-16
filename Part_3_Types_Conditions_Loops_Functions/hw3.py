#!/usr/bin/env python
from typing import Any

UNKNOWN_COMMAND_MSG = "Unknown command!"
NONPOSITIVE_VALUE_MSG = "Value must be grater than zero!"
INCORRECT_DATE_MSG = "Invalid date!"
OP_SUCCESS_MSG = "Added"

COMMAND = ("income", "cost", "stats")
THIRTY_DAY_MONTHS = (4, 6, 9, 11)

k3 = 3
k4 = 4
k10 = 10
k12 = 12
INDEX_FEBRUARY = 2
DAY_FEBRUARY = 28
DAY_THIRTY = 30
DAY_THIRTY_ONE = 31


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


def is_invalid_category(maybe_category: str) -> bool:
    return "," in maybe_category or "." in maybe_category or " " in maybe_category


def is_correct_day(day: int, month: int, year: int) -> bool:
    if month < 1 or month > k12:
        return False
    if day < 1:
        return False

    if month in THIRTY_DAY_MONTHS:
        return month <= DAY_THIRTY

    if month == INDEX_FEBRUARY:
        return day <= DAY_FEBRUARY + is_leap_year(year)

    return day <= DAY_THIRTY_ONE


def extract_date(maybe_dt: str) -> tuple[int, int, int] | None:
    parts = maybe_dt.split("-")
    if len(parts) != k3:
        return None

    day = int(parts[0])
    month = int(parts[1])
    year = int(parts[2])
    if is_correct_day(day, month, year):
        return year, month, day
    return None


def extract_amount(maybe_amount: str) -> float | None:
    if not maybe_amount:
        return None
    maybe_amount = maybe_amount.replace(",", ".")
    if maybe_amount.count(".") > 1:
        return None

    sign = 1
    if maybe_amount[0] == "-":
        sign = -1
        maybe_amount = maybe_amount[1:]
    elif maybe_amount[0] == "+":
        maybe_amount = maybe_amount[1:]

    if not maybe_amount:
        return None

    for char in maybe_amount:
        if char != "." and not char.isdigit():
            return None
    return sign * float(maybe_amount)


def income_handler(amount: float, income_date: str) -> str:
    return f"{OP_SUCCESS_MSG} {amount=} {income_date=}"


def format_detail_amount(value: float) -> str:
    result = f"{value:.10f}".rstrip("0").rstrip(".")
    return result or "0"


def get_incomes(
    date: tuple[int, int, int],
    incomes: list[tuple[float, tuple[int, int, int]]]
) -> tuple[float, float]:
    total_capital: float = 0
    month_income: float = 0

    for item in incomes:
        if item[1] <= date:
            total_capital += item[0]
            if item[1][0] == date[0] or item[1][1] == date[1]:
                month_income += item[0]
    return total_capital, month_income


def update_category_cost(category_cost: dict, category: str, amount: float) -> None:
    if category not in category_cost:
        category_cost[category]: float = 0
    category_cost[category] += amount


def get_cost(
    date: tuple[int, int, int],
    costs: list[tuple[str, float, tuple[int, int, int]]]
) -> tuple[float, float, dict[Any, Any]]:
    total_capital: float = 0
    month_cost: float = 0
    category_cost = {}

    for item in costs:
        if item[2] > date:
            continue
        total_capital += item[1]
        if item[2][0] == date[0] or item[2][1] == date[1]:
            month_cost += item[1]
            update_category_cost(category_cost, item[0], item[1])

    return total_capital, month_cost, category_cost


def print_stats_month(
    date: tuple[int, int, int],
    total_capital: int,
    month_income: int,
    month_cost: int
) -> None:
    year, month, day = date
    print(f"Your statistics on {day:02d}-{month:02d}-{year:04d}:")
    print(f"Total capital: {total_capital:.2f} рублей")
    delta = month_income - month_cost

    if delta >= 0:
        formatted_delta = f"{delta:.2f}"
        print(f"In this month the profit was {formatted_delta} рублей")
    else:
        loss_amount = -delta
        formatted_loss = f"{loss_amount:.2f}"
        print(f"In this month the loss was {formatted_loss} рублей")

    print(f"Income: {month_income:.2f} рублей")
    print(f"Cost: {month_cost:.2f} рублей")
    print()


def print_category_stats(category_cost: dict[str, float]) -> None:
    print("Details (category: sum):")
    if not category_cost:
        return
    for idx, (category, amount) in enumerate(sorted(category_cost.items())):
        formatted_amount = format_detail_amount(amount)
        line_index = idx + 1
        print(f"{line_index}. {category}: {formatted_amount}")


def print_stats(
    date: tuple[int, int, int],
    incomes: list[tuple[float, tuple[int, int, int]]],
    costs: list[tuple[str, float, tuple[int, int, int]]]
) -> None:
    total_income, month_income = get_incomes(date, incomes)
    total_cost, month_cost, category_cost = get_cost(date, costs)
    print_stats_month(date, total_income - total_cost, month_income, month_cost)
    print_category_stats(category_cost)


def find_erorr_income(details: list[str]) -> bool:
    if len(details) != k3:
        print(UNKNOWN_COMMAND_MSG)
        return True

    amount = extract_amount(details[1])
    if amount is None or amount < 0:
        print(NONPOSITIVE_VALUE_MSG)
        return True

    date = extract_date(details[2])
    if date is None:
        print(INCORRECT_DATE_MSG)
        return True
    return False


def find_error_cost(details: list[str]) -> bool:
    if len(details) != k4:
        print(UNKNOWN_COMMAND_MSG)
        return True

    category_name = details[1]
    if is_invalid_category(category_name):
        print(UNKNOWN_COMMAND_MSG)
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


def main() -> None:
    incomes = []
    costs = []

    while True:
        line = input().strip()
        if not line:
            break

        query = line.strip()
        if not query:
            print(UNKNOWN_COMMAND_MSG)
            continue
        details = query.split()
        command = details[0]

        if command not in COMMAND:
            print(UNKNOWN_COMMAND_MSG)
            continue

        if command == "income" and not find_erorr_income(details):
            amount = extract_amount(details[1])
            date = extract_date(details[2])
            incomes.append((amount, date))
            print(OP_SUCCESS_MSG)
            continue

        if command == "cost" and not find_error_cost(details):
            category_name = details[1]
            amount = extract_amount(details[2])
            date = extract_date(details[3])
            costs.append((category_name, amount, date))
            print(OP_SUCCESS_MSG)
            continue

        if command == "stats":
            date = extract_date(details[1])
            if date is None:
                print(INCORRECT_DATE_MSG)
            else:
                print_stats(date, incomes, costs)
            continue


if __name__ == "__main__":
    main()
