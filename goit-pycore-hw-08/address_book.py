from collections import UserDict
from datetime import date, datetime, timedelta
from typing import Dict, List, Optional

DATE_FORMAT = "%d.%m.%Y"  # DD.MM.YYYY


class Field:
    """Base class for record fields."""

    def __init__(self, value):
        self.value = value

    def __str__(self) -> str:
        return str(self.value)


class Name(Field):
    """Contact name. Required field, cannot be empty."""

    def __init__(self, value: str):
        if not value or not value.strip():
            raise ValueError("Name cannot be empty.")
        super().__init__(value.strip())


class Phone(Field):
    """Phone number that must contain exactly 10 digits."""

    def __init__(self, value: str):
        if not (isinstance(value, str) and value.isdigit() and len(value) == 10):
            raise ValueError(f"Invalid phone '{value}'. Phone must contain exactly 10 digits.")
        super().__init__(value)


class Birthday(Field):
    """Birthday stored as a date; created from a 'DD.MM.YYYY' string."""

    def __init__(self, value: str):
        try:
            birthday = datetime.strptime(value, DATE_FORMAT).date()
        except (TypeError, ValueError):
            raise ValueError("Invalid date format. Use DD.MM.YYYY")
        if birthday > date.today():
            raise ValueError("Birthday cannot be in the future.")
        super().__init__(birthday)

    def __str__(self) -> str:
        return self.value.strftime(DATE_FORMAT)


class Record:
    """Contact: a name, a list of phones and an optional birthday."""

    def __init__(self, name: str):
        self.name = Name(name)
        self.phones: List[Phone] = []
        self.birthday: Optional[Birthday] = None

    def add_phone(self, phone: str) -> None:
        """Add a new phone; the same number is not stored twice."""
        if self.find_phone(phone) is None:
            self.phones.append(Phone(phone))

    def find_phone(self, phone: str) -> Optional[Phone]:
        """Return the Phone object with this number or None."""
        for item in self.phones:
            if item.value == phone:
                return item
        return None

    def remove_phone(self, phone: str) -> None:
        item = self.find_phone(phone)
        if item is None:
            raise ValueError(f"Phone {phone} not found.")
        self.phones.remove(item)

    def edit_phone(self, old_phone: str, new_phone: str) -> None:
        """Replace old_phone with new_phone, keeping its position in the list."""
        item = self.find_phone(old_phone)
        if item is None:
            raise ValueError(f"Phone {old_phone} not found for {self.name}.")
        # Validate the new number before changing anything
        self.phones[self.phones.index(item)] = Phone(new_phone)

    def add_birthday(self, birthday: str) -> None:
        """Set the birthday (a contact has only one, so a new one replaces the old)."""
        self.birthday = Birthday(birthday)

    def __str__(self) -> str:
        phones = "; ".join(p.value for p in self.phones) or "no phones"
        text = f"Contact name: {self.name.value}, phones: {phones}"
        if self.birthday:
            text += f", birthday: {self.birthday}"
        return text


def _birthday_in_year(birthday: date, year: int) -> date:
    """Birthday in the given year (29 Feb becomes 1 Mar in non-leap years)."""
    try:
        return birthday.replace(year=year)
    except ValueError:
        return date(year, 3, 1)


class AddressBook(UserDict):
    """Stores records by contact name."""

    def add_record(self, record: Record) -> None:
        self.data[record.name.value] = record

    def find(self, name: str) -> Optional[Record]:
        return self.data.get(name)

    def delete(self, name: str) -> None:
        self.data.pop(name, None)

    def get_upcoming_birthdays(self, days: int = 7) -> List[Dict[str, str]]:
        """Who to congratulate during the next `days` days, including today.

        A birthday on Saturday or Sunday is moved to the following Monday.
        Returns a list of {'name': ..., 'congratulation_date': 'DD.MM.YYYY'}
        sorted by date.
        """
        today = date.today()
        upcoming = []

        for record in self.data.values():
            if record.birthday is None:
                continue

            birthday = _birthday_in_year(record.birthday.value, today.year)
            if birthday < today:
                birthday = _birthday_in_year(record.birthday.value, today.year + 1)

            if (birthday - today).days >= days:
                continue

            if birthday.weekday() == 5:  # Saturday
                birthday += timedelta(days=2)
            elif birthday.weekday() == 6:  # Sunday
                birthday += timedelta(days=1)

            upcoming.append({"name": record.name.value, "congratulation_date": birthday})

        upcoming.sort(key=lambda item: item["congratulation_date"])
        return [
            {"name": item["name"], "congratulation_date": item["congratulation_date"].strftime(DATE_FORMAT)}
            for item in upcoming
        ]

    def __str__(self) -> str:
        if not self.data:
            return "Address book is empty."
        return "\n".join(str(record) for record in self.data.values())
