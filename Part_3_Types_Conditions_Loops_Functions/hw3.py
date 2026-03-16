#!/usr/bin/env python

UNKNOWN_COMMAND_MSG = "Unknown command!"
NONPOSITIVE_VALUE_MSG = "Value must be grater than zero!"
INCORRECT_DATE_MSG = "Invalid date!"
OP_SUCCESS_MSG = "Added"

THIRTY_DAY_MONTHS = (4, 6, 9, 11)

k3 = 3
k4 = 4
k10 = 10
k12 = 12
INDEX_FEBRUARY = 1
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


def is_correct_day(year: int, month: int, day: int) -> bool:
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

    year = int(parts[0])
    month = int(parts[1])
    day = int(parts[2])
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
        if char != "." or not char.isdigit():
            return None
    return sign * float(maybe_amount)


def income_handler(amount: float, income_date: str) -> str:
    return f"{OP_SUCCESS_MSG} {amount=} {income_date=}"


def format_detail_amount(value: float) -> str:
    result = f"{value:.10f}".rstrip("0").rstrip(".")
    return result or "0"


def calculate_totals_by_date(
    items: list,
    target_date: tuple[int, int, int],
    is_income: bool = True) -> tuple[float, float]:
    """
    Вычисляет общую сумму и сумму за указанный месяц.

    Args:
        items: список транзакций
        target_date: целевая дата (день, месяц, год)
        is_income: True для доходов, False для расходов

    Returns:
        (total_amount, monthly_amount)
    """
    total = 0.0
    monthly = 0.0
    day, month, year = target_date

    for item in items:
        if is_income:
            amount, cur_day, cur_month, cur_year = item
        else:
            category, amount, cur_day, cur_month, cur_year = item

        if (cur_year, cur_month, cur_day) < target_date:
            total += amount
            if cur_year == year or cur_month == month:
                monthly += amount

    return total, monthly


def process_cost_categories(
    costs: list,
    target_date: tuple[int, int, int]) -> dict:
    """
    Обрабатывает расходы по категориям.

    Args:
        costs: список расходов
        target_date: целевая дата

    Returns:
        словарь с суммами по категориям
    """
    categories = {}
    year, month, _ = target_date

    for category, amount, cur_day, cur_month, cur_year in costs:
        if (cur_year, cur_month, cur_day) < target_date:
            if cur_year == year or cur_month == month:
                categories[category] = categories.get(category, 0.0) + amount

    return categories


def format_amount(amount: float) -> str:
    return f"{amount:.2f}"


def print_period_stats(
    total_capital: float,
    month_income: float,
    month_cost: float,
    delta: float) -> None:
    """Печатает статистику за период."""
    print(f"Total capital: {format_amount(total_capital)} рублей")

    if delta >= 0:
        print(f"In this month the profit was {format_amount(delta)} рублей")
    else:
        print(f"In this month the loss was {format_amount(-delta)} рублей")

    print(f"Income: {format_amount(month_income)} рублей")
    print(f"Cost: {format_amount(month_cost)} рублей")


def print_category_stats(categories: dict) -> None:
    """Печатает статистику по категориям."""
    print()
    print("Details (category: sum):")

    sorted_categories = sorted(categories.items())
    for idx, (category, amount) in enumerate(sorted_categories):
        formatted_amount = format_detail_amount(amount)
        line_index = idx + 1
        print(f"{line_index}. {category}: {formatted_amount}")


def print_stats(date: tuple[int, int, int], incomes: list, costs: list) -> None:
    """
    Печатает полную статистику.

    Args:
        date: текущая дата (день, месяц, год)
        incomes: список доходов
        costs: список расходов
    """
    day, month, year = date

    total_income, month_income = calculate_totals_by_date(incomes, date, True)
    total_cost, month_cost = calculate_totals_by_date(costs, date, False)

    categories = process_cost_categories(costs, date)
    total_capital = total_income - total_cost
    delta = month_income - month_cost

    print(f"Your statistics on {day:02d}-{month:02d}-{year:04d}:")
    print_period_stats(total_capital, month_income, month_cost, delta)
    print_category_stats(categories)


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
