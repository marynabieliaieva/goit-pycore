import os
import pickle
from pathlib import Path
from typing import Union

from address_book import AddressBook

# The file lives next to the program, so the data is found whatever the current directory is
DEFAULT_FILE = Path(__file__).resolve().parent / "addressbook.pkl"

PathLike = Union[str, Path]


def save_data(book: AddressBook, filename: PathLike = DEFAULT_FILE) -> None:
    """Serialize the address book to a file with pickle.

    The data is written to a temporary file first and then moved in place,
    so an interrupted save never leaves a broken file behind.
    """
    path = Path(filename)
    tmp_path = path.with_name(path.name + ".tmp")
    with open(tmp_path, "wb") as f:
        pickle.dump(book, f)
    os.replace(tmp_path, path)


def load_data(filename: PathLike = DEFAULT_FILE) -> AddressBook:
    """Restore the address book from a file.

    Returns a new empty AddressBook if the file does not exist yet.
    If the file cannot be read as a saved address book, it is renamed to
    '<name>.bak' (so the next save does not overwrite it) and an empty
    AddressBook is returned.
    """
    path = Path(filename)
    try:
        with open(path, "rb") as f:
            book = pickle.load(f)
    except FileNotFoundError:
        return AddressBook()
    except Exception as error:  # a damaged pickle can raise almost any exception
        return _start_empty(path, f"could not read it ({type(error).__name__}: {error})")

    if not isinstance(book, AddressBook):
        return _start_empty(path, "it does not contain an address book")
    return book


def _start_empty(path: Path, reason: str) -> AddressBook:
    """Keep an unreadable data file as a backup and return an empty book."""
    backup = path.with_name(path.name + ".bak")
    os.replace(path, backup)
    print(f"Saved data in {path.name} was not loaded: {reason}. "
          f"The file was kept as {backup.name}. Starting with an empty address book.")
    return AddressBook()
