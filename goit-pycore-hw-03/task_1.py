from datetime import datetime
from typing import Optional


def get_days_from_today(date: str) -> Optional[int]:
    """Return the number of days from the given date to today.

    The date must be a string in 'YYYY-MM-DD' format. Only calendar days are
    counted, the time of day is ignored. A date later than today gives a
    negative result. Returns None if the date has the wrong format.
    """
    try:
        given_date = datetime.strptime(date, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        print(f"Invalid date '{date}'. Expected format: YYYY-MM-DD")
        return None

    today = datetime.today().date()
    return (today - given_date).days


if __name__ == "__main__":
    print(get_days_from_today("2021-10-09"))
    print(get_days_from_today("2100-01-01"))
    print(get_days_from_today("09.10.2021"))
