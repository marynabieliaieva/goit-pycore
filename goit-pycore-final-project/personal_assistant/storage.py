"""Saving data to disk with pickle, in a folder inside the user's home.

By default the data lives in ``~/.personal_assistant``. Set the
``PERSONAL_ASSISTANT_HOME`` environment variable to use another folder.
"""

import os
import pickle
from pathlib import Path
from typing import Callable, TypeVar

from .contacts import AddressBook
from .notes import NoteBook

APP_DIR_NAME = ".personal_assistant"
CONTACTS_FILE = "contacts.pkl"
NOTES_FILE = "notes.pkl"

T = TypeVar("T")


def data_dir() -> Path:
    """The folder with the data files; it is created if missing."""
    folder = Path(
        os.environ.get("PERSONAL_ASSISTANT_HOME") or Path.home() / APP_DIR_NAME
    )
    folder.mkdir(parents=True, exist_ok=True)
    return folder


def save(obj, filename: str) -> Path:
    """Pickle ``obj`` into the data folder.

    The data goes to a temporary file first and then replaces the old file,
    so an interrupted save never leaves a half-written file.
    """
    path = data_dir() / filename
    tmp_path = path.with_name(path.name + ".tmp")
    with open(tmp_path, "wb") as f:
        pickle.dump(obj, f)
    os.replace(tmp_path, path)
    return path


def load(filename: str, factory: Callable[[], T]) -> T:
    """Unpickle an object from the data folder.

    Returns ``factory()`` (a new empty object) if the file does not exist.
    If the file is damaged or holds something else, it is kept as
    '<name>.bak' so it is not overwritten, and an empty object is returned.
    """
    path = data_dir() / filename
    expected = type(factory())
    try:
        with open(path, "rb") as f:
            obj = pickle.load(f)
    except FileNotFoundError:
        return factory()
    except Exception as error:
        # A damaged pickle can raise almost any exception
        return _start_empty(path, factory, f"{type(error).__name__}: {error}")
    if not isinstance(obj, expected):
        return _start_empty(
            path,
            factory,
            f"expected {expected.__name__}, found {type(obj).__name__}",
        )
    return obj


def _start_empty(path: Path, factory: Callable[[], T], reason: str) -> T:
    backup = path.with_name(path.name + ".bak")
    os.replace(path, backup)
    print(
        f"Warning: could not read {path} ({reason}). "
        f"It was kept as {backup.name}; starting empty."
    )
    return factory()


def load_contacts() -> AddressBook:
    return load(CONTACTS_FILE, AddressBook)


def load_notes() -> NoteBook:
    return load(NOTES_FILE, NoteBook)


def save_all(book: AddressBook, notes: NoteBook) -> None:
    save(book, CONTACTS_FILE)
    save(notes, NOTES_FILE)
