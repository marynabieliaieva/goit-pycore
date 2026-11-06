import sys
from collections import Counter
from pathlib import Path
from typing import Dict, List

LogRecord = Dict[str, str]

LEVELS = ("INFO", "DEBUG", "ERROR", "WARNING")


def parse_log_line(line: str) -> LogRecord:
    """Split a log line into date, time, level and message.

    Raises ValueError if the line does not match the expected format:
    'YYYY-MM-DD HH:MM:SS LEVEL message'.
    """
    parts = line.strip().split(" ", 3)
    if len(parts) < 4:
        raise ValueError(f"Invalid log line: {line.strip()!r}")
    date, time, level, message = parts
    return {"date": date, "time": time, "level": level.upper(), "message": message}


def load_logs(file_path: str) -> List[LogRecord]:
    """Read the log file and parse every non-empty line."""
    logs: List[LogRecord] = []
    with open(file_path, "r", encoding="utf-8") as file:
        for number, line in enumerate(file, start=1):
            if not line.strip():
                continue
            try:
                logs.append(parse_log_line(line))
            except ValueError as error:
                # Skip broken lines but tell the user about them
                print(f"Line {number} skipped: {error}", file=sys.stderr)
    return logs


def filter_logs_by_level(logs: List[LogRecord], level: str) -> List[LogRecord]:
    """Return only the records of the given level (case-insensitive)."""
    level = level.upper()
    return list(filter(lambda record: record["level"] == level, logs))


def count_logs_by_level(logs: List[LogRecord]) -> Dict[str, int]:
    """Count records for each logging level."""
    counter = Counter(record["level"] for record in logs)
    # Known levels go first (even with zero records), then any other levels
    counts = {level: counter.get(level, 0) for level in LEVELS}
    counts.update({lvl: n for lvl, n in counter.items() if lvl not in counts})
    return counts


def display_log_counts(counts: Dict[str, int]) -> None:
    """Print the counts as a table."""
    print(f"{'Рівень логування':<17}| Кількість")
    print(f"{'-' * 17}|{'-' * 10}")
    for level, count in counts.items():
        print(f"{level:<17}| {count}")


def display_log_details(logs: List[LogRecord], level: str) -> None:
    """Print all records of one level."""
    print(f"\nДеталі логів для рівня '{level.upper()}':")
    if not logs:
        print("Записів не знайдено.")
    for record in logs:
        print(f"{record['date']} {record['time']} - {record['message']}")


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python task_3.py path/to/logfile.log [level]")
        sys.exit(1)

    file_path = sys.argv[1]
    level = sys.argv[2] if len(sys.argv) > 2 else None

    if not Path(file_path).is_file():
        print(f"Файл не знайдено: {file_path}")
        sys.exit(1)

    try:
        logs = load_logs(file_path)
    except (OSError, UnicodeDecodeError) as error:
        print(f"Не вдалося прочитати файл: {error}")
        sys.exit(1)

    display_log_counts(count_logs_by_level(logs))

    if level:
        display_log_details(filter_logs_by_level(logs, level), level)


if __name__ == "__main__":
    main()
