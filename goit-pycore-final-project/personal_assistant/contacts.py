"""Contacts: a ``Record`` per person and the ``AddressBook`` of them."""

from collections import UserDict
from datetime import date
from typing import List, Optional, Tuple

from .fields import Address, Birthday, Email, Name, Phone


class Record:
    """A contact. Composed of validated fields:

    a required ``Name``, any number of ``Phone`` objects and optional
    ``Email``, ``Address`` and ``Birthday``.
    """

    def __init__(self, name: str):
        self.name = Name(name)
        self.phones: List[Phone] = []
        self.email: Optional[Email] = None
        self.address: Optional[Address] = None
        self.birthday: Optional[Birthday] = None

    # --- phones -------------------------------------------------------------

    def find_phone(self, phone: str) -> Optional[Phone]:
        """Return the stored Phone equal to ``phone`` or None."""
        wanted = Phone(phone)
        for item in self.phones:
            if item == wanted:
                return item
        return None

    def add_phone(self, phone: str) -> bool:
        """Add a phone. Returns False if the contact already has it."""
        if self.find_phone(phone) is not None:
            return False
        self.phones.append(Phone(phone))
        return True

    def edit_phone(self, old_phone: str, new_phone: str) -> None:
        """Replace ``old_phone`` with ``new_phone`` at the same position."""
        item = self.find_phone(old_phone)
        if item is None:
            raise ValueError(f"{self.name} has no phone {old_phone}.")
        new_item = Phone(new_phone)  # validate before changing anything
        if new_item != item and new_item in self.phones:
            raise ValueError(f"{self.name} already has phone {new_item}.")
        self.phones[self.phones.index(item)] = new_item

    def remove_phone(self, phone: str) -> None:
        item = self.find_phone(phone)
        if item is None:
            raise ValueError(f"{self.name} has no phone {phone}.")
        self.phones.remove(item)

    # --- other fields -------------------------------------------------------

    def set_email(self, email: str) -> None:
        self.email = Email(email)

    def set_address(self, address: str) -> None:
        self.address = Address(address)

    def set_birthday(self, birthday: str) -> None:
        self.birthday = Birthday(birthday)

    def matches(self, query: str) -> bool:
        """True if ``query`` occurs in any field (case-insensitive).

        Phones are compared by digits, so '050-123' finds '0501234567'.
        """
        query = query.strip().lower()
        if not query:
            return False
        texts = [
            self.name.value,
            str(self.email or ""),
            str(self.address or ""),
            str(self.birthday or ""),
        ]
        if any(query in text.lower() for text in texts):
            return True
        digits = "".join(ch for ch in query if ch.isdigit())
        return bool(digits) and any(
            digits in phone.value for phone in self.phones
        )

    def days_to_birthday(self, today: Optional[date] = None) -> Optional[int]:
        """Days until the next birthday (0 = today), or None if no birthday."""
        if self.birthday is None:
            return None
        today = today or date.today()
        next_birthday = birthday_in_year(self.birthday.value, today.year)
        if next_birthday < today:
            next_birthday = birthday_in_year(
                self.birthday.value, today.year + 1
            )
        return (next_birthday - today).days

    def __str__(self) -> str:
        lines = [f"Name:     {self.name}"]
        lines.append(
            f"Phones:   {', '.join(p.value for p in self.phones) or '-'}"
        )
        lines.append(f"Email:    {self.email or '-'}")
        lines.append(f"Address:  {self.address or '-'}")
        lines.append(f"Birthday: {self.birthday or '-'}")
        return "\n".join(lines)


def birthday_in_year(birthday: date, year: int) -> date:
    """The birthday in ``year``; 29 Feb becomes 1 Mar in non-leap years."""
    try:
        return birthday.replace(year=year)
    except ValueError:
        return date(year, 3, 1)


class AddressBook(UserDict):
    """All contacts, stored by name. Name lookup is case-insensitive."""

    def _key(self, name: str) -> Optional[str]:
        """The stored key for ``name`` regardless of letter case, or None."""
        wanted = name.strip().lower()
        for key in self.data:
            if key.lower() == wanted:
                return key
        return None

    def add_record(self, record: Record) -> None:
        if self._key(record.name.value) is not None:
            raise ValueError(f"Contact '{record.name}' already exists.")
        self.data[record.name.value] = record

    def find(self, name: str) -> Optional[Record]:
        key = self._key(name)
        return self.data[key] if key is not None else None

    def delete(self, name: str) -> Record:
        key = self._key(name)
        if key is None:
            raise KeyError(f"Contact '{name}' not found.")
        return self.data.pop(key)

    def rename(self, old_name: str, new_name: str) -> None:
        record = self.find(old_name)
        if record is None:
            raise KeyError(f"Contact '{old_name}' not found.")
        new = Name(new_name)
        existing = self._key(new.value)
        if existing is not None and existing != record.name.value:
            raise ValueError(f"Contact '{new}' already exists.")
        del self.data[record.name.value]
        record.name = new
        self.data[new.value] = record

    def search(self, query: str) -> List[Record]:
        """Contacts with ``query`` in any field."""
        return [
            record for record in self.sorted_records() if record.matches(query)
        ]

    def sorted_records(self) -> List[Record]:
        return sorted(self.data.values(), key=lambda r: r.name.value.lower())

    def upcoming_birthdays(
        self, days: int, today: Optional[date] = None
    ) -> List[Tuple[Record, int]]:
        """Contacts with a birthday within ``days`` days from today.

        Today counts as day 0, so ``days=7`` covers the next 7 days.

        Returns (record, days_left) pairs sorted by days_left.
        """
        if days < 0:
            raise ValueError("Number of days cannot be negative.")
        result = []
        for record in self.data.values():
            left = record.days_to_birthday(today)
            if left is not None and left <= days:
                result.append((record, left))
        result.sort(key=lambda item: (item[1], item[0].name.value.lower()))
        return result
