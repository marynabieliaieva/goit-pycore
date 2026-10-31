from datetime import date, datetime, timedelta

DAYS_AHEAD = 7  # today + the next 6 days


def birthday_in_year(birthday: date, year: int) -> date:
    """Return the birthday in the given year (29 Feb becomes 1 Mar in non-leap years)."""
    try:
        return birthday.replace(year=year)
    except ValueError:
        return date(year, 3, 1)


def get_upcoming_birthdays(users: list[dict]) -> list[dict]:
    """Return who to congratulate during the next 7 days, including today.

    Each user is a dict with 'name' and 'birthday' ('YYYY.MM.DD'). A birthday
    on Saturday or Sunday is moved to the following Monday. The result is a
    list of dicts with 'name' and 'congratulation_date' ('YYYY.MM.DD').
    """
    today = datetime.today().date()
    upcoming = []

    for user in users:
        birthday = datetime.strptime(user["birthday"], "%Y.%m.%d").date()

        birthday_this_year = birthday_in_year(birthday, today.year)
        if birthday_this_year < today:
            birthday_this_year = birthday_in_year(birthday, today.year + 1)

        days_until = (birthday_this_year - today).days
        if days_until >= DAYS_AHEAD:
            continue

        congratulation_date = birthday_this_year
        if congratulation_date.weekday() == 5:  # Saturday
            congratulation_date += timedelta(days=2)
        elif congratulation_date.weekday() == 6:  # Sunday
            congratulation_date += timedelta(days=1)

        upcoming.append(
            {
                "name": user["name"],
                "congratulation_date": congratulation_date.strftime("%Y.%m.%d"),
            }
        )

    return upcoming


if __name__ == "__main__":
    users = [
        {"name": "John Doe", "birthday": "1985.01.23"},
        {"name": "Jane Smith", "birthday": "1990.01.27"},
    ]

    upcoming_birthdays = get_upcoming_birthdays(users)
    print("Список привітань на цьому тижні:", upcoming_birthdays)
