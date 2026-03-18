#!/usr/bin/env python

UNKNOWN_COMMAND_MSG = "Unknown command!"
NONPOSITIVE_VALUE_MSG = "Value must be grater than zero!"
INCORRECT_DATE_MSG = "Invalid date!"
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


def is_earlier(first_date: Date, second_date: Date) -> bool:
    first_day, first_month, first_year = first_date
    second_day, second_month, second_year = second_date
    return (first_year, first_month, first_day) <= (
        second_year,
        second_month,
        second_day,
    )


def is_same_month(first_date: Date, second_date: Date) -> bool:
    return first_date[1] == second_date[1] and first_date[2] == second_date[2]


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

    for category, amount, cost_date in costs:
        if is_earlier(cost_date, date):
            total_cost += amount
            if is_same_month(cost_date, date):
                month_cost += amount
                if category not in category_cost:
                    category_cost[category] = float(0)
                category_cost[category] += amount

    return total_cost, month_cost, category_cost


def print_delta(month_income: float, month_cost: float) -> None:
    delta = month_income - month_cost
    if delta >= 0:
        print(f"In this month the profit was {delta:.2f} рублей")
        return

    print(f"In this month the loss was {-delta:.2f} рублей")


def print_category_stats(category_cost: dict[str, float]) -> None:
    print()
    print("Details (category: sum):")
    for idx, (category, amount) in enumerate(sorted(category_cost.items()), start=1):
        formatted_amount = format_detail_amount(amount)
        print(f"{idx}. {category}: {formatted_amount}")


def print_stats(date: Date, incomes: list[Income], costs: list[Cost]) -> None:
    income_stats = collect_income_stats(date, incomes)
    cost_stats = collect_cost_stats(date, costs)

    day, month, year = date
    total_capital = income_stats[0] - cost_stats[0]

    print(f"Your statistics on {day:02d}-{month:02d}-{year:04d}:")
    print(f"Total capital: {total_capital:.2f} рублей")
    print_delta(income_stats[1], cost_stats[1])
    print(f"Income: {income_stats[1]:.2f} рублей")
    print(f"Cost: {cost_stats[1]:.2f} рублей")
    print_category_stats(cost_stats[2])


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


def handle_income(details: list[str], incomes: list[Income]) -> None:
    if find_erorr_income(details):
        return

    amount = extract_amount(details[1])
    date = extract_date(details[2])
    if amount is None or date is None:
        return

    incomes.append((amount, date))
    print(OP_SUCCESS_MSG)


def handle_cost(details: list[str], costs: list[Cost]) -> None:
    if find_error_cost(details):
        return

    category_name = details[1]
    amount = extract_amount(details[2])
    date = extract_date(details[3])
    if amount is None or date is None:
        return

    costs.append((category_name, amount, date))
    print(OP_SUCCESS_MSG)


def handle_stats(details: list[str], incomes: list[Income], costs: list[Cost]) -> None:
    if len(details) != LEN_INCOME - 1:
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
