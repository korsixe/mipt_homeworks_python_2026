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
STATS_ARGS_COUNT: int = 2


class Date:
    def __init__(self, day: int, month: int, year: int) -> None:
        self._day: int = day
        self._month: int = month
        self._year: int = year

    @property
    def day(self) -> int:
        return self._day

    @property
    def month(self) -> int:
        return self._month

    @property
    def year(self) -> int:
        return self._year

    def __le__(self, other: "Date") -> bool:
        if self.year != other.year:
            return self.year < other.year
        if self.month != other.month:
            return self.month < other.month
        return self.day <= other.day

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Date):
            return NotImplemented
        return (self.year == other.year and
                self.month == other.month and
                self.day == other.day)

    def __hash__(self) -> int:
        return hash((self.year, self.month, self.day))

    def same_month(self, other: "Date") -> bool:
        return self.year == other.year and self.month == other.month


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
        extra: int = 1 if is_leap_year(year) else 0
        return day <= DAY_FEBRUARY + extra
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
    processed: str = maybe_amount.replace(",", ".")
    if processed.count(".") > 1:
        return None
    sign: int = 1
    if processed[0] == "-":
        sign = -1
        processed = processed[1:]
    elif processed[0] == "+":
        processed = processed[1:]
    if not processed:
        return None
    for ch in processed:
        if ch != "." and not ch.isdigit():
            return None
    return sign * float(processed)


def format_detail_amount(value: float) -> str:
    result: str = f"{value:.10f}".rstrip("0").rstrip(".")
    return result or "0"


def sum_incomes(date: Date, incomes: list[Income]) -> tuple[float, float]:
    total: float = 0
    monthly: float = 0
    for inc in incomes:
        if inc.date <= date:
            total += inc.amount
            if inc.date.same_month(date):
                monthly += inc.amount
    return total, monthly


def _update_cat(cat_dict: dict[str, float], cat: str, val: float) -> None:
    if cat not in cat_dict:
        cat_dict[cat] = 0
    cat_dict[cat] += val


def _process_cost_item(
    cst: Cost,
    date: Date,
    total: float,
    monthly: float,
    by_cat: dict[str, float]
) -> tuple[float, float]:
    total += cst.amount
    if cst.date.same_month(date):
        monthly += cst.amount
        _update_cat(by_cat, cst.category, cst.amount)
    return total, monthly


def sum_costs(date: Date, costs: list[Cost]) -> tuple[float, float, dict[str, float]]:
    total: float = 0
    monthly: float = 0
    by_cat: dict[str, float] = {}
    for cst in costs:
        if cst.date <= date:
            total, monthly = _process_cost_item(cst, date, total, monthly, by_cat)
    return total, monthly, by_cat


def _print_header(dt: Date) -> None:
    day_str: str = f"{dt.day:02d}"
    month_str: str = f"{dt.month:02d}"
    year_str: str = f"{dt.year:04d}"
    print(f"Your statistics on {day_str}-{month_str}-{year_str}:")


def _print_capital(capital: float) -> None:
    print(f"Total capital: {capital:.2f} рублей")


def _print_delta(inc: float, cost: float) -> None:
    delta: float = inc - cost
    if delta >= 0:
        profit: float = delta
        print(f"In this month the profit was {profit:.2f} рублей")
    else:
        loss: float = -delta
        print(f"In this month the loss was {loss:.2f} рублей")


def _print_income_cost(inc: float, cost: float) -> None:
    print(f"Income: {inc:.2f} рублей")
    print(f"Cost: {cost:.2f} рублей")
    print()


def display_monthly_stats(dt: Date, capital: float, inc: float, cost: float) -> None:
    _print_header(dt)
    _print_capital(capital)
    _print_delta(inc, cost)
    _print_income_cost(inc, cost)


def show_category_breakdown(cat_data: dict[str, float]) -> None:
    print("Details (category):")
    if not cat_data:
        return
    sorted_cats: list[tuple[str, float]] = sorted(cat_data.items())
    for pos, (cat, val) in enumerate(sorted_cats):
        index: int = pos + 1
        formatted: str = format_detail_amount(val)
        print(f"{index}. {cat}: {formatted}")


def show_full_stats(dt: Date, inc_list: list[Income], cst_list: list[Cost]) -> None:
    total_inc, month_inc = sum_incomes(dt, inc_list)
    total_cost, month_cost, cats = sum_costs(dt, cst_list)
    capital: float = total_inc - total_cost
    display_monthly_stats(dt, capital, month_inc, month_cost)
    show_category_breakdown(cats)


def _check_income_len(details: list[str]) -> bool:
    if len(details) != k3:
        print(UNKNOWN_COMMAND_MSG)
        return False
    return True


def _check_cost_len(details: list[str]) -> bool:
    if len(details) != k4:
        print(UNKNOWN_COMMAND_MSG)
        return False
    return True


def _get_validated_income(details: list[str]) -> tuple[float, Date] | None:
    if not _check_income_len(details):
        return None
    amount_val: float | None = extract_amount(details[1])
    if amount_val is None or amount_val < 0:
        print(NONPOSITIVE_VALUE_MSG)
        return None
    date_val: Date | None = extract_date(details[2])
    if date_val is None:
        print(INCORRECT_DATE_MSG)
        return None
    return (amount_val, date_val)


def _get_validated_cost(details: list[str]) -> tuple[str, float, Date] | None:
    if not _check_cost_len(details):
        return None
    cat_val: str = details[1]
    if is_invalid_category(cat_val):
        print(UNKNOWN_COMMAND_MSG)
        return None
    amount_val: float | None = extract_amount(details[2])
    if amount_val is None or amount_val <= 0:
        print(NONPOSITIVE_VALUE_MSG)
        return None
    date_val: Date | None = extract_date(details[3])
    if date_val is None:
        print(INCORRECT_DATE_MSG)
        return None
    return (cat_val, amount_val, date_val)


def handle_income(details: list[str], storage: list[Income]) -> bool:
    validated: tuple[float, Date] | None = _get_validated_income(details)
    if validated is None:
        return False
    amount, date = validated
    storage.append(Income(amount, date))
    print(OP_SUCCESS_MSG)
    return True


def handle_cost(details: list[str], storage: list[Cost]) -> bool:
    validated: tuple[str, float, Date] | None = _get_validated_cost(details)
    if validated is None:
        return False
    cat, amount, date = validated
    storage.append(Cost(cat, amount, date))
    print(OP_SUCCESS_MSG)
    return True


def handle_stats(details: list[str], inc_list: list[Income], cst_list: list[Cost]) -> bool:
    if len(details) != STATS_ARGS_COUNT:
        print(INCORRECT_DATE_MSG)
        return False
    date: Date | None = extract_date(details[1])
    if date is None:
        print(INCORRECT_DATE_MSG)
        return False
    show_full_stats(date, inc_list, cst_list)
    return True


def main() -> None:
    incomes: list[Income] = []
    costs: list[Cost] = []

    while True:
        line: str = input().strip()
        if not line:
            break
        tokens: list[str] = line.split()
        cmd: str = tokens[0]

        if cmd == "income":
            handle_income(tokens, incomes)
        elif cmd == "cost":
            handle_cost(tokens, costs)
        elif cmd == "stats":
            handle_stats(tokens, incomes, costs)
        else:
            print(UNKNOWN_COMMAND_MSG)


if __name__ == "__main__":
    main()
