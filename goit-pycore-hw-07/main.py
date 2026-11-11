from functools import wraps
from typing import Callable, List, Tuple

from address_book import AddressBook, Record


def input_error(func: Callable[..., str]) -> Callable[..., str]:
    """Turn input errors raised in a handler into messages for the user."""

    @wraps(func)
    def inner(*args, **kwargs) -> str:
        try:
            return func(*args, **kwargs)
        except ValueError as error:
            # Validation errors: wrong phone, wrong date, unknown phone
            return str(error)
        except IndexError as error:
            # Not enough arguments; the handler passes a usage hint
            return str(error) if error.args else "Enter the argument for the command"
        except KeyError as error:
            # Contact does not exist
            return error.args[0] if error.args else "Contact not found."

    return inner


def parse_input(user_input: str) -> Tuple[str, ...]:
    """Split user input into a lowercase command and its arguments."""
    parts = user_input.split()
    if not parts:
        return ("",)
    cmd, *args = parts
    return (cmd.strip().lower(), *args)


def require_args(args: List[str], count: int, usage: str) -> None:
    """Raise IndexError with a usage hint if there are too few arguments."""
    if len(args) < count:
        raise IndexError(f"Not enough arguments. Usage: {usage}")


def get_record(book: AddressBook, name: str) -> Record:
    """Return the record or raise KeyError with a readable message."""
    record = book.find(name)
    if record is None:
        raise KeyError(f"Contact '{name}' not found.")
    return record


@input_error
def add_contact(args: List[str], book: AddressBook) -> str:
    # Both the name and the phone are required
    require_args(args, 2, "add [name] [phone]")
    name, phone, *_ = args
    record = book.find(name)
    message = "Contact updated."
    if record is None:
        record = Record(name)
        message = "Contact added."
    record.add_phone(phone)  # validated before the contact is saved
    book.add_record(record)
    return message


@input_error
def change_contact(args: List[str], book: AddressBook) -> str:
    require_args(args, 3, "change [name] [old phone] [new phone]")
    name, old_phone, new_phone, *_ = args
    get_record(book, name).edit_phone(old_phone, new_phone)
    return "Phone changed."


@input_error
def show_phone(args: List[str], book: AddressBook) -> str:
    require_args(args, 1, "phone [name]")
    record = get_record(book, args[0])
    if not record.phones:
        return f"{record.name} has no phones."
    return f"{record.name}: {'; '.join(p.value for p in record.phones)}"


@input_error
def show_all(args: List[str], book: AddressBook) -> str:
    return str(book)


@input_error
def add_birthday(args: List[str], book: AddressBook) -> str:
    require_args(args, 2, "add-birthday [name] [DD.MM.YYYY]")
    name, birthday, *_ = args
    get_record(book, name).add_birthday(birthday)
    return "Birthday added."


@input_error
def show_birthday(args: List[str], book: AddressBook) -> str:
    require_args(args, 1, "show-birthday [name]")
    record = get_record(book, args[0])
    if record.birthday is None:
        return f"{record.name} has no birthday saved."
    return f"{record.name}: {record.birthday}"


@input_error
def birthdays(args: List[str], book: AddressBook) -> str:
    upcoming = book.get_upcoming_birthdays()
    if not upcoming:
        return "No birthdays in the next 7 days."
    return "\n".join(f"{item['congratulation_date']}: {item['name']}" for item in upcoming)


def main() -> None:
    book = AddressBook()
    print("Welcome to the assistant bot!")
    while True:
        try:
            user_input = input("Enter a command: ")
        except (EOFError, KeyboardInterrupt):
            print("\nGood bye!")
            break
        command, *args = parse_input(user_input)

        if command in ["close", "exit"]:
            print("Good bye!")
            break

        elif command == "hello":
            print("How can I help you?")

        elif command == "add":
            print(add_contact(args, book))

        elif command == "change":
            print(change_contact(args, book))

        elif command == "phone":
            print(show_phone(args, book))

        elif command == "all":
            print(show_all(args, book))

        elif command == "add-birthday":
            print(add_birthday(args, book))

        elif command == "show-birthday":
            print(show_birthday(args, book))

        elif command == "birthdays":
            print(birthdays(args, book))

        elif command == "":
            continue

        else:
            print("Invalid command.")


if __name__ == "__main__":
    main()
