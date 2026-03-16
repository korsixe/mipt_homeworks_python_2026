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

    def __eq__(self, other: "Date") -> bool:
        if not isinstance(other, Date):
            return False
        return (self.year == other.year and
                self.month == other.month and
                self.day == other.day)

    def __hash__(self) -> int:
        return hash((self.year, self.month, self.day))

    def same_month(self, other: "Date") -> bool:
        return self.year == other.year and self.month == other.month

    def to_tuple(self) -> tuple[int, int, int]:
        return (self.year, self.month, self.day)

    @classmethod
    def from_tuple(cls, date_tuple: tuple[int, int, int]) -> "Date":
        year: int
        month: int
        day: int
        year, month, day = date_tuple
        return cls(day, month, year)


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


def sum_incomes_up_to_date(date: Date, incomes: list[Income]) -> tuple[float, float]:
    total: float = 0
    monthly: float = 0

    for inc in incomes:
        if inc.date <= date:
            total += inc.amount
            if inc.date.same_month(date):
                monthly += inc.amount
    return total, monthly


def add_to_category(cat_dict: dict[str, float], cat: str, val: float) -> None:
    if cat not in cat_dict:
        cat_dict[cat] = 0
    cat_dict[cat] += val


def sum_costs_up_to_date(date: Date, costs: list[Cost]) -> tuple[float, float, dict[str, float]]:
    total: float = 0
    monthly: float = 0
    by_category: dict[str, float] = {}

    for cst in costs:
        if cst.date <= date:
            total += cst.amount
            if cst.date.same_month(date):
                monthly += cst.amount
                add_to_category(by_category, cst.category, cst.amount)

    return total, monthly, by_category


def display_monthly_stats(
    dt: Date,
    capital: float,
    inc_month: float,
    cost_month: float
) -> None:
    day_str: str = f"{dt.day:02d}"
    month_str: str = f"{dt.month:02d}"
    year_str: str = f"{dt.year:04d}"
    print(f"Your statistics on {day_str}-{month_str}-{year_str}:")
    print(f"Total capital: {capital:.2f} рублей")
    delta: float = inc_month - cost_month

    if delta >= 0:
        formatted: str = f"{delta:.2f}"
        print(f"In this month the profit was {formatted} рублей")
    else:
        loss: float = -delta
        formatted_loss: str = f"{loss:.2f}"
        print(f"In this month the loss was {formatted_loss} рублей")

    print(f"Income: {inc_month:.2f} рублей")
    print(f"Cost: {cost_month:.2f} рублей")
    print()


def show_category_breakdown(cat_data: dict[str, float]) -> None:
    print("Details (category: sum):")
    if not cat_data:
        return

    sorted_cats: list[tuple[str, float]] = sorted(cat_data.items())
    for pos, (cat, val) in enumerate(sorted_cats):
        formatted: str = format_detail_amount(val)
        idx: int = pos + 1
        print(f"{idx}. {cat}: {formatted}")


def show_full_stats(dt: Date, inc_list: list[Income], cst_list: list[Cost]) -> None:
    total_inc, month_inc = sum_incomes_up_to_date(dt, inc_list)
    total_cst, month_cst, cat_data = sum_costs_up_to_date(dt, cst_list)
    total_cap: float = total_inc - total_cst
    display_monthly_stats(dt, total_cap, month_inc, month_cst)
    show_category_breakdown(cat_data)


def handle_income(details: list[str], storage: list[Income]) -> bool:
    value: float | None = extract_amount(details[1])
    dt_obj: Date | None = extract_date(details[2])
    if value is not None and dt_obj is not None:
        storage.append(Income(value, dt_obj))
        print(OP_SUCCESS_MSG)
        return True
    return False


def handle_cost(details: list[str], storage: list[Cost]) -> bool:
    value: float | None = extract_amount(details[2])
    dt_obj: Date | None = extract_date(details[3])
    if value is not None and dt_obj is not None:
        storage.append(Cost(details[1], value, dt_obj))
        print(OP_SUCCESS_MSG)
        return True
    return False


def handle_stats(details: list[str], inc_list: list[Income], cst_list: list[Cost]) -> bool:
    dt_obj: Date | None = extract_date(details[1])
    if dt_obj is None:
        print(INCORRECT_DATE_MSG)
        return False
    show_full_stats(dt_obj, inc_list, cst_list)
    return True


def validate_income(details: list[str]) -> bool:
    if len(details) != k3:
        print(UNKNOWN_COMMAND_MSG)
        return True

    amount_val: float | None = extract_amount(details[1])
    if amount_val is None or amount_val < 0:
        print(NONPOSITIVE_VALUE_MSG)
        return True

    date_val: Date | None = extract_date(details[2])
    if date_val is None:
        print(INCORRECT_DATE_MSG)
        return True
    return False


def validate_cost(details: list[str]) -> bool:
    if len(details) != k4:
        print(UNKNOWN_COMMAND_MSG)
        return True

    category: str = details[1]
    if is_invalid_category(category):
        print(UNKNOWN_COMMAND_MSG)
        return True

    amount_val: float | None = extract_amount(details[2])
    if amount_val is None or amount_val <= 0:
        print(NONPOSITIVE_VALUE_MSG)
        return True

    date_val: Date | None = extract_date(details[3])
    if date_val is None:
        print(INCORRECT_DATE_MSG)
        return True
    return False


def main() -> None:
    incomes: list[Income] = []
    costs: list[Cost] = []

    while True:
        raw: str = input().strip()
        if not raw:
            break

        cleaned: str = raw.strip()
        if not cleaned:
            print(UNKNOWN_COMMAND_MSG)
            continue

        tokens: list[str] = cleaned.split()
        cmd: str = tokens[0]

        if cmd not in COMMAND:
            print(UNKNOWN_COMMAND_MSG)
            continue

        if cmd == "income":
            if not validate_income(tokens):
                handle_income(tokens, incomes)

        elif cmd == "cost":
            if not validate_cost(tokens):
                handle_cost(tokens, costs)

        elif cmd == "stats":
            handle_stats(tokens, incomes, costs)


if __name__ == "__main__":
    main()