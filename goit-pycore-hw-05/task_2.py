import re
from typing import Callable, Iterator

# A real number with a fractional part, surrounded by whitespace
# (or the start/end of the text) on both sides.
NUMBER_PATTERN = re.compile(r"(?<!\S)\d+\.\d+(?!\S)")


def generator_numbers(text: str) -> Iterator[float]:
    """Yield every real number found in the text one by one."""
    for match in NUMBER_PATTERN.finditer(text):
        yield float(match.group())


def sum_profit(text: str, func: Callable[[str], Iterator[float]]) -> float:
    """Sum all numbers produced by the generator function `func`."""
    # round() removes floating point noise like 1351.4600000000001
    return round(sum(func(text)), 2)


if __name__ == "__main__":
    text = (
        "Загальний дохід працівника складається з декількох частин: "
        "1000.01 як основний дохід, доповнений додатковими надходженнями "
        "27.45 і 324.00 доларів."
    )
    total_income = sum_profit(text, generator_numbers)
    print(f"Загальний дохід: {total_income}")
