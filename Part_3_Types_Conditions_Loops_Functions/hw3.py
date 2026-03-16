#!/usr/bin/env python

UNKNOWN_COMMAND_MSG = "Unknown command!"
NONPOSITIVE_VALUE_MSG = "Value must be grater than zero!"
INCORRECT_DATE_MSG = "Invalid date!"
OP_SUCCESS_MSG = "Added"
DAYS_IN_MOUNTH_LONG_YEAR = [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
DAYS_IN_MOUNTH_BASE_YEAR = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

k3 = 3
k4 = 4
k10 = 10
k12 = 12


def is_leap_year(year: int) -> bool:
    """
    Для заданного года определяет: високосный (True) или невисокосный (False).

    :param int year: Проверяемый год
    :return: Значение високосности.
    :rtype: bool
    """
    return (year % 4 == 0) and (year % 100 != 0 or year % 400 == 0)


def is_invalid_category(maybe_category: str) -> bool:
    return "," in maybe_category or "." in maybe_category or " " in maybe_category


def extract_date(maybe_dt: str) -> tuple[int, int, int] | None:
    """
    Парсит дату формата DD-MM-YYYY из строки.

    :param str maybe_dt: Проверяемая строка
    :return: typle формата (день, месяц, год) или None, если дата неправильная.
    :rtype: tuple[int, int, int] | None
    """
    parts = maybe_dt.split("-")
    if len(parts) != k3:
        return None

    year = int(parts[0])
    month = int(parts[1])
    day = int(parts[2])
    if month < 1 or month > k12:
        return None
    if day < 1:
        return None

    if is_leap_year(year) and day > DAYS_IN_MOUNTH_LONG_YEAR[month - 1]:
        return None
    if not (is_leap_year(year)) and day > DAYS_IN_MOUNTH_BASE_YEAR[month - 1]:
        return None
    return year, month, day


def extract_amount(maybe_amount: str) -> float | None:
    if not maybe_amount:
        return None

    if maybe_amount.count(",") + maybe_amount.count(".") > 1:
        return None

    sign = 1
    if maybe_amount[0] == "-":
        sign = -1
        maybe_amount = maybe_amount[1:]
    elif maybe_amount[0] == "+":
        maybe_amount = maybe_amount[1:]

    if not maybe_amount:
        return None

    separate = False
    integer = 0
    fractional = 0

    for char in maybe_amount:
        if char in [".", ","]:
            separate = True
        elif char.isdigit():
            digit = ord(char) - ord("0")
            if separate:
                fractional = fractional * k10 + digit
            else:
                integer = integer * k10 + digit
        else:
            return None

    return sign * (integer + fractional / 10 ** len(
        str(fractional))) if fractional > 0 else sign * integer


def income_handler(amount: float, income_date: str) -> str:
    return f"{OP_SUCCESS_MSG} {amount=} {income_date=}"


def format_detail_amount(value: float) -> str:
    result = f"{value:.10f}".rstrip("0").rstrip(".")
    return result or "0"


def print_stats(date: tuple[int, int, int],
    incomes: list[tuple[float, int, int, int]],
    costs: list[tuple[str, float, int, int, int]]) -> None:
    day, month, year = date
    total_capital = 0.0
    month_cost = 0.0
    month_income = 0.0
    category_cost = {}

    for amount, cur_day, cur_month, cur_year in incomes:
        if (cur_year, cur_month, cur_day) < (year, month, day):
            total_capital += amount
            if cur_year == year or cur_month == month:
                month_income += amount

    for category, amount, cur_day, cur_month, cur_year in costs:
        if (cur_year, cur_month, cur_day) < (year, month, day):
            total_capital -= amount
            if cur_year == year or cur_month == month:
                month_cost += amount
                if category not in category_cost:
                    category_cost[category] = 0.0
                category_cost[category] += amount

    delta = month_income - month_cost
    print(f"Your statistics on {day:02d}-{month:02d}-{year:04d}:")
    print(f"Total capital: {total_capital:.2f} рублей")

    if delta >= 0:
        print(f"In this month the profit was {delta:.2f} рублей")
    else:
        print(f"In this month the loss was {(-delta):.2f} рублей")

    print(f"Income: {month_income:.2f} рублей")
    print(f"Cost: {month_cost:.2f} рублей")
    print()
    print("Details (category: sum):")

    sorted_categories = sorted(category_cost.keys())
    for index in range(len(sorted_categories)):
        category = sorted_categories[index]
        print(
            f"{index + 1}. {category}: {format_detail_amount(sorted_categories[category])}")


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

    with open(0) as file:
        for line in file:
            query = line.strip()
            if not query:
                print(UNKNOWN_COMMAND_MSG)
                continue
            details = query.split()
            command = query[0]

            if command == "income" and not find_erorr_income(details):
                amount = extract_amount(details[1])
                date = extract_date(details[2])
                day, month, year = date
                incomes.append((amount, day, month, year))
                print(OP_SUCCESS_MSG)

            if command == "cost" and not find_error_cost(details):
                category_name = details[1]
                amount = extract_amount(details[2])
                date = extract_date(details[3])
                day, month, year = date
                costs.append((category_name, amount, day, month, year))
                print(OP_SUCCESS_MSG)

            if command == "stats":
                date = extract_date(details[1])
                if date is None:
                    print(INCORRECT_DATE_MSG)
                    continue
                print_stats(date, incomes, costs)


if __name__ == "__main__":
    main()
