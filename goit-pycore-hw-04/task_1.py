from pathlib import Path
from typing import Tuple, Union


def total_salary(path: Union[str, Path]) -> Tuple[int, float]:
    """Return the total and average salary from a 'Name,salary' file.

    Malformed lines are skipped with a warning. If the file is missing,
    unreadable or has no valid lines, returns (0, 0).
    """
    salaries = []
    try:
        with open(path, "r", encoding="utf-8") as file:
            for line_number, line in enumerate(file, start=1):
                line = line.strip()
                if not line:
                    continue
                try:
                    _, salary = line.split(",")
                    salaries.append(int(salary))
                except ValueError:
                    print(f"Skipping malformed line {line_number}: '{line}'")
    except FileNotFoundError:
        print(f"File not found: {path}")
        return 0, 0
    except (OSError, UnicodeDecodeError) as error:
        print(f"Cannot read file {path}: {error}")
        return 0, 0

    if not salaries:
        return 0, 0

    total = sum(salaries)
    average = total / len(salaries)
    return total, average


if __name__ == "__main__":
    salary_file = Path(__file__).parent / "data" / "salary_file.txt"
    total, average = total_salary(salary_file)
    print(f"Загальна сума заробітної плати: {total}, Середня заробітна плата: {average:g}")
