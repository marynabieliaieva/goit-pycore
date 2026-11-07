from collections import UserDict
from typing import List, Optional


class Field:
    """Base class for record fields."""

    def __init__(self, value: str):
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
            raise ValueError(f"Phone number must contain exactly 10 digits: {value!r}")
        super().__init__(value)


class Record:
    """Contact: a name and a list of phones."""

    def __init__(self, name: str):
        self.name = Name(name)
        self.phones: List[Phone] = []

    def add_phone(self, phone: str) -> None:
        """Add a new phone (validated by the Phone class)."""
        self.phones.append(Phone(phone))

    def find_phone(self, phone: str) -> Optional[Phone]:
        """Return the Phone object with this number or None."""
        for item in self.phones:
            if item.value == phone:
                return item
        return None

    def remove_phone(self, phone: str) -> None:
        """Remove a phone; raise ValueError if it is not in the record."""
        item = self.find_phone(phone)
        if item is None:
            raise ValueError(f"Phone {phone} not found.")
        self.phones.remove(item)

    def edit_phone(self, old_phone: str, new_phone: str) -> None:
        """Replace old_phone with new_phone, keeping its position in the list."""
        item = self.find_phone(old_phone)
        if item is None:
            raise ValueError(f"Phone {old_phone} not found.")
        # Validate the new number before changing anything
        self.phones[self.phones.index(item)] = Phone(new_phone)

    def __str__(self) -> str:
        return f"Contact name: {self.name.value}, phones: {'; '.join(p.value for p in self.phones)}"


class AddressBook(UserDict):
    """Stores records by contact name."""

    def add_record(self, record: Record) -> None:
        self.data[record.name.value] = record

    def find(self, name: str) -> Optional[Record]:
        return self.data.get(name)

    def delete(self, name: str) -> None:
        """Delete a record by name; do nothing if it does not exist."""
        self.data.pop(name, None)


if __name__ == "__main__":
    # Створення нової адресної книги
    book = AddressBook()

    # Створення запису для John
    john_record = Record("John")
    john_record.add_phone("1234567890")
    john_record.add_phone("5555555555")

    # Додавання запису John до адресної книги
    book.add_record(john_record)

    # Створення та додавання нового запису для Jane
    jane_record = Record("Jane")
    jane_record.add_phone("9876543210")
    book.add_record(jane_record)

    # Виведення всіх записів у книзі
    for name, record in book.data.items():
        print(record)

    # Знаходження та редагування телефону для John
    john = book.find("John")
    john.edit_phone("1234567890", "1112223333")

    print(john)  # Contact name: John, phones: 1112223333; 5555555555

    # Пошук конкретного телефону в записі John
    found_phone = john.find_phone("5555555555")
    print(f"{john.name}: {found_phone}")  # John: 5555555555

    # Видалення запису Jane
    book.delete("Jane")
