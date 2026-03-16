#!/usr/bin/env python

UNKNOWN_COMMAND_MSG: str = "Unknown command!"
NONPOSITIVE_VALUE_MSG: str = "Value must be grater than zero!"
INCORRECT_DATE_MSG: str = "Invalid date!"
OP_SUCCESS_MSG: str = "Added"

COMMAND: tuple[str, str, str] = ("income", "cost", "stats")
THIRTY_DAY_MONTHS: tuple[int, int, int, int] = (4, 6, 9, 11)

k3: int = 3
k4: int = 4
k10: int = 10
k12: int = 12
INDEX_FEBRUARY: int = 2
DAY_FEBRUARY: int = 28
DAY_THIRTY: int = 30
DAY_THIRTY_ONE: int = 31


class Date:
    def __init__(self, day: int, month: int, year: int) -> None:
        self.day: int = day
        self.month: int = month
        self.year: int = year

    def __le__(self, other: "Date") -> bool:
        if self.year != other.year:
            return self.year < other.year
        if self.month != other.month:
            return self.month < other.month
        return self.day <= other.day

    def __eq__(self, other: "Date") -> bool:
        return (self.year == other.year and
                self.month == other.month and
                self.day == other.day)

    def __hash__(self) -> int:
        return hash((self.year, self.month, self.day))

    def same_month(self, other: "Date") -> bool:
        return self.year == other.year and self.month == other.month

    def to_tuple(self) -> tuple[int, int, int]:
        return (self.year, self.month, self.day)

    @staticmethod
    def from_tuple(date_tuple: tuple[int, int, int]) -> "Date":
        year: int
        month: int
        day: int
        year, month, day = date_tuple
        return Date(day, month, year)


class Income:
    def __init__(self, amount: float, date: Date) -> None:
        self.amount: float = amount
        self.date: Date = date


class Cost:
    def __init__(self, category: str, amount: float, date: Date) -> None:
        self.category: str = category
        self.amount: float = amount
        self.date: Date = date


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
    has_comma: bool = "," in maybe_category
    has_dot: bool = "." in maybe_category
    has_space: bool = " " in maybe_category
    return has_comma or has_dot or has_space


def is_correct_day(day: int, month: int, year: int) -> bool:
    if month < 1 or month > k12:
        return False
    if day < 1:
        return False

    if month in THIRTY_DAY_MONTHS:
        return day <= DAY_THIRTY

    if month == INDEX_FEBRUARY:
        max_days: int = DAY_FEBRUARY + is_leap_year(year)
        return day <= max_days

    return day <= DAY_THIRTY_ONE


def extract_date(maybe_dt: str) -> Date | None:
    parts: list[str] = maybe_dt.split("-")
    if len(parts) != k3:
        return None

    day: int = int(parts[0])
    month: int = int(parts[1])
    year: int = int(parts[2])
    if is_correct_day(day, month, year):
        return Date(day, month, year)
    return None


def extract_amount(maybe_amount: str) -> float | None:
    if not maybe_amount:
        return None
    maybe_amount = maybe_amount.replace(",", ".")
    if maybe_amount.count(".") > 1:
        return None

    sign: int = 1
    if maybe_amount[0] == "-":
        sign = -1
        maybe_amount = maybe_amount[1:]
    elif maybe_amount[0] == "+":
        maybe_amount = maybe_amount[1:]

    if not maybe_amount:
        return None

    char: str
    for char in maybe_amount:
        if char != "." and not char.isdigit():
            return None
    return sign * float(maybe_amount)


def income_handler(amount: float, income_date: Date) -> str:
    day_str: str = f"{income_date.day:02d}"
    month_str: str = f"{income_date.month:02d}"
    year_str: str = f"{income_date.year:04d}"
    return f"{OP_SUCCESS_MSG} {amount=} {day_str}-{month_str}-{year_str}"


def format_detail_amount(value: float) -> str:
    result: str = f"{value:.10f}".rstrip("0").rstrip(".")
    return result or "0"


def get_incomes(date: Date, incomes: list[Income]) -> tuple[float, float]:
    total_capital: float = 0.0
    month_income: float = 0.0

    income: Income
    for income in incomes:
        if income.date <= date:
            total_capital += income.amount
            if income.date.same_month(date):
                month_income += income.amount
    return total_capital, month_income


def update_category_cost(category_cost: dict[str, float], category: str,
    amount: float) -> None:
    if category not in category_cost:
        category_cost[category] = 0.0
    category_cost[category] += amount


def get_cost(date: Date, costs: list[Cost]) -> tuple[
    float, float, dict[str, float]]:
    total_capital: float = 0.0
    month_cost: float = 0.0
    category_cost: dict[str, float] = {}

    cost: Cost
    for cost in costs:
        if cost.date <= date:
            total_capital += cost.amount
            if cost.date.same_month(date):
                month_cost += cost.amount
                update_category_cost(category_cost, cost.category, cost.amount)

    return total_capital, month_cost, category_cost


def print_stats_month(
    date: Date,
    total_capital: float,
    month_income: float,
    month_cost: float
) -> None:
    day_str: str = f"{date.day:02d}"
    month_str: str = f"{date.month:02d}"
    year_str: str = f"{date.year:04d}"
    print(f"Your statistics on {day_str}-{month_str}-{year_str}:")
    print(f"Total capital: {total_capital:.2f} рублей")
    delta: float = month_income - month_cost

    if delta >= 0:
        formatted_delta: str = f"{delta:.2f}"
        print(f"In this month the profit was {formatted_delta} рублей")
    else:
        loss_amount: float = -delta
        formatted_loss: str = f"{loss_amount:.2f}"
        print(f"In this month the loss was {formatted_loss} рублей")

    print(f"Income: {month_income:.2f} рублей")
    print(f"Cost: {month_cost:.2f} рублей")
    print()


def print_category_stats(category_cost: dict[str, float]) -> None:
    print("Details (category: sum):")
    if not category_cost:
        return

    sorted_items: list[tuple[str, float]] = sorted(category_cost.items())
    idx: int
    category: str
    amount: float
    for idx, (category, amount) in enumerate(sorted_items):
        formatted_amount: str = format_detail_amount(amount)
        line_index: int = idx + 1
        print(f"{line_index}. {category}: {formatted_amount}")


def print_stats(date: Date, incomes: list[Income], costs: list[Cost]) -> None:
    total_income: float
    month_income: float
    total_income, month_income = get_incomes(date, incomes)

    total_cost: float
    month_cost: float
    category_cost: dict[str, float]
    total_cost, month_cost, category_cost = get_cost(date, costs)

    total_capital: float = total_income - total_cost
    print_stats_month(date, total_capital, month_income, month_cost)
    print_category_stats(category_cost)


def process_income_command(details: list[str], incomes: list[Income]) -> bool:
    amount_str: str = details[1]
    amount: float | None = extract_amount(amount_str)
    date_str: str = details[2]
    date: Date | None = extract_date(date_str)
    if amount is not None and date is not None:
        incomes.append(Income(amount, date))
        print(income_handler(amount, date))
        return True
    return False


def process_cost_command(details: list[str], costs: list[Cost]) -> bool:
    category_name: str = details[1]
    amount_str: str = details[2]
    amount: float | None = extract_amount(amount_str)
    date_str: str = details[3]
    date: Date | None = extract_date(date_str)
    if amount is not None and date is not None:
        costs.append(Cost(category_name, amount, date))
        print(OP_SUCCESS_MSG)
        return True
    return False


def process_stats_command(details: list[str], incomes: list[Income],
    costs: list[Cost]) -> bool:
    date_str: str = details[1]
    date: Date | None = extract_date(date_str)
    if date is None:
        print(INCORRECT_DATE_MSG)
        return False
    print_stats(date, incomes, costs)
    return True


def find_error_income(details: list[str]) -> bool:
    if len(details) != k3:
        print(UNKNOWN_COMMAND_MSG)
        return True

    amount_str: str = details[1]
    amount: float | None = extract_amount(amount_str)
    if amount is None or amount < 0:
        print(NONPOSITIVE_VALUE_MSG)
        return True

    date_str: str = details[2]
    date: Date | None = extract_date(date_str)
    if date is None:
        print(INCORRECT_DATE_MSG)
        return True
    return False


def find_error_cost(details: list[str]) -> bool:
    if len(details) != k4:
        print(UNKNOWN_COMMAND_MSG)
        return True

    category_name: str = details[1]
    if is_invalid_category(category_name):
        print(UNKNOWN_COMMAND_MSG)
        return True

    amount_str: str = details[2]
    amount: float | None = extract_amount(amount_str)
    if amount is None or amount <= 0:
        print(NONPOSITIVE_VALUE_MSG)
        return True

    date_str: str = details[3]
    date: Date | None = extract_date(date_str)
    if date is None:
        print(INCORRECT_DATE_MSG)
        return True
    return False


def main() -> None:
    incomes: list[Income] = []
    costs: list[Cost] = []

    while True:
        line: str = input().strip()
        if not line:
            break

        query: str = line.strip()
        if not query:
            print(UNKNOWN_COMMAND_MSG)
            continue
        details: list[str] = query.split()
        command: str = details[0]

        if command not in COMMAND:
            print(UNKNOWN_COMMAND_MSG)
            continue

        if command == "income":
            if find_error_income(details):
                continue
            process_income_command(details, incomes)
            continue

        if command == "cost":
            if find_error_cost(details):
                continue
            process_cost_command(details, costs)
            continue

        if command == "stats":
            process_stats_command(details, incomes, costs)
            continue


if __name__ == "__main__":
    main()
