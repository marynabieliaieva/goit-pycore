"""Validated fields of a contact and of a note.

Every field checks its value in ``__init__`` and raises ``ValueError`` with a
message that can be shown to the user as is. A field object always holds a
valid value: to change a value, create a new field object.
"""

import re
from datetime import date, datetime

DATE_FORMAT = "%d.%m.%Y"  # DD.MM.YYYY

NAME_MAX_LENGTH = 50
ADDRESS_MAX_LENGTH = 200
NOTE_MAX_LENGTH = 1000
TAG_MAX_LENGTH = 30

# local-part@domain.tld, no spaces, at least one dot in the domain
EMAIL_PATTERN = re.compile(
    r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}$"
)
# Separators that may be typed inside a phone number and are ignored
PHONE_SEPARATORS = re.compile(r"[\s\-().]")
TAG_PATTERN = re.compile(r"^[\w-]+$")


class Field:
    """Base class for all fields: stores a value and prints it."""

    def __init__(self, value):
        self.value = value

    def __str__(self) -> str:
        return str(self.value)

    def __eq__(self, other) -> bool:
        return isinstance(other, type(self)) and self.value == other.value

    def __hash__(self) -> int:
        return hash((type(self).__name__, self.value))


class Name(Field):
    """Contact name: required, one word up to 50 characters."""

    def __init__(self, value: str):
        value = (value or "").strip()
        if not value:
            raise ValueError("Name cannot be empty.")
        if len(value) > NAME_MAX_LENGTH:
            raise ValueError(
                f"Name is too long (max {NAME_MAX_LENGTH} characters)."
            )
        super().__init__(value)


class Phone(Field):
    """Phone number of exactly 10 digits.

    Spaces, dashes, dots and parentheses are allowed while typing and are
    removed, so ``(050) 123-45-67`` is stored as ``0501234567``.
    """

    def __init__(self, value: str):
        digits = PHONE_SEPARATORS.sub("", value or "")
        if not (digits.isdigit() and len(digits) == 10):
            raise ValueError(
                f"Invalid phone '{value}'. Phone must contain exactly "
                "10 digits, e.g. 0501234567."
            )
        super().__init__(digits)


class Email(Field):
    """E-mail address in the form name@domain.tld, stored in lowercase."""

    def __init__(self, value: str):
        value = (value or "").strip()
        if not EMAIL_PATTERN.match(value):
            raise ValueError(
                f"Invalid email '{value}'. Use the form name@example.com."
            )
        super().__init__(value.lower())


class Address(Field):
    """Postal address: free text up to 200 characters."""

    def __init__(self, value: str):
        value = " ".join((value or "").split())  # collapse repeated spaces
        if not value:
            raise ValueError("Address cannot be empty.")
        if len(value) > ADDRESS_MAX_LENGTH:
            raise ValueError(
                f"Address is too long (max {ADDRESS_MAX_LENGTH} characters)."
            )
        super().__init__(value)


class Birthday(Field):
    """Birthday stored as a ``date``; created from a 'DD.MM.YYYY' string."""

    def __init__(self, value: str):
        try:
            birthday = datetime.strptime(value, DATE_FORMAT).date()
        except (TypeError, ValueError):
            raise ValueError(
                f"Invalid date '{value}'. Use DD.MM.YYYY, e.g. 15.05.1990."
            ) from None
        if birthday > date.today():
            raise ValueError("Birthday cannot be in the future.")
        super().__init__(birthday)

    def __str__(self) -> str:
        return self.value.strftime(DATE_FORMAT)


class NoteText(Field):
    """Text of a note: required, up to 1000 characters."""

    def __init__(self, value: str):
        value = (value or "").strip()
        if not value:
            raise ValueError("Note text cannot be empty.")
        if len(value) > NOTE_MAX_LENGTH:
            raise ValueError(
                f"Note is too long (max {NOTE_MAX_LENGTH} characters)."
            )
        super().__init__(value)


class Tag(Field):
    """Note tag: one word of letters, digits, '_' or '-', stored in lowercase.

    A leading '#' is accepted and removed: '#Work' and 'work' are one tag.
    """

    def __init__(self, value: str):
        value = (value or "").strip().lstrip("#").lower()
        if not value or not TAG_PATTERN.match(value):
            raise ValueError(
                f"Invalid tag '{value}'. Use one word of letters, "
                "digits, '_' or '-'."
            )
        if len(value) > TAG_MAX_LENGTH:
            raise ValueError(
                f"Tag is too long (max {TAG_MAX_LENGTH} characters)."
            )
        super().__init__(value)
