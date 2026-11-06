from functools import wraps
from typing import Callable, Dict, List, Tuple

Contacts = Dict[str, str]


def input_error(func: Callable[..., str]) -> Callable[..., str]:
    """Turn user input errors raised in a handler into messages for the user."""

    @wraps(func)
    def inner(*args, **kwargs) -> str:
        try:
            return func(*args, **kwargs)
        except ValueError:
            # Wrong number of arguments, e.g. "add" or "add Bob"
            return "Enter the argument for the command"
        except IndexError:
            # A required argument is missing, e.g. "phone"
            return "Enter the argument for the command"
        except KeyError:
            # The contact does not exist
            return "Contact not found."

    return inner


def parse_input(user_input: str) -> Tuple[str, ...]:
    """Split user input into a lowercase command and its arguments."""
    parts = user_input.split()
    if not parts:
        return ("",)
    cmd, *args = parts
    return (cmd.strip().lower(), *args)


@input_error
def add_contact(args: List[str], contacts: Contacts) -> str:
    name, phone = args  # ValueError if not exactly two arguments
    contacts[name] = phone
    return "Contact added."


@input_error
def change_contact(args: List[str], contacts: Contacts) -> str:
    name, phone = args  # ValueError if not exactly two arguments
    if name not in contacts:
        raise KeyError(name)
    contacts[name] = phone
    return "Contact updated."


@input_error
def show_phone(args: List[str], contacts: Contacts) -> str:
    name = args[0]  # IndexError if the name is missing
    return contacts[name]  # KeyError if the contact does not exist


@input_error
def show_all(contacts: Contacts) -> str:
    if not contacts:
        return "No contacts saved."
    return "\n".join(f"{name}: {phone}" for name, phone in contacts.items())


def main() -> None:
    contacts: Contacts = {}
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, *args = parse_input(user_input)

        if command in ["close", "exit"]:
            print("Good bye!")
            break
        elif command == "hello":
            print("How can I help you?")
        elif command == "add":
            print(add_contact(args, contacts))
        elif command == "change":
            print(change_contact(args, contacts))
        elif command == "phone":
            print(show_phone(args, contacts))
        elif command == "all":
            print(show_all(contacts))
        else:
            print("Invalid command.")


if __name__ == "__main__":
    main()
