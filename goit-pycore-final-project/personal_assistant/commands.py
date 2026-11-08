"""Command handlers and the command registry.

Each handler takes the list of arguments typed after the command and the
``Context`` with the address book and the notebook, and returns the text to
print. Input errors are turned into messages by ``input_error``, so a wrong
command never stops the program.
"""

import re
from dataclasses import dataclass
from functools import wraps
from typing import Callable, Dict, List, Optional

from .contacts import AddressBook, Record
from .fields import Tag
from .notes import Note, NoteBook

DEFAULT_BIRTHDAY_DAYS = 7
INLINE_TAG = re.compile(r"^#[\w-]+$")


@dataclass
class Context:
    """Data the handlers work with."""

    book: AddressBook
    notes: NoteBook


Handler = Callable[[List[str], Context], str]


@dataclass
class Command:
    """A command the user can type."""

    handler: Handler
    usage: str
    description: str
    group: str
    changes_data: bool = False


COMMANDS: Dict[str, Command] = {}
ALIASES: Dict[str, str] = {}


class UsageError(Exception):
    """Wrong number of arguments; the message shows the right usage."""


def input_error(func: Handler) -> Handler:
    """Turn input errors raised in a handler into messages for the user."""

    @wraps(func)
    def inner(args: List[str], ctx: Context) -> str:
        try:
            return func(args, ctx)
        except UsageError as error:
            return f"Not enough arguments. Usage: {error}"
        except KeyError as error:
            return error.args[0] if error.args else "Not found."
        except ValueError as error:
            return str(error)

    return inner


def command(
    name: str,
    usage: str,
    description: str,
    group: str,
    changes_data: bool = False,
    aliases: tuple = (),
) -> Callable[[Handler], Handler]:
    """Register a handler under ``name`` (and its aliases)."""

    def decorator(func: Handler) -> Handler:
        wrapped = input_error(func)
        COMMANDS[name] = Command(
            wrapped, usage, description, group, changes_data
        )
        for alias in aliases:
            ALIASES[alias] = name
        return wrapped

    return decorator


def resolve(name: str) -> Optional[Command]:
    """The Command for a typed name or alias, or None."""
    return COMMANDS.get(ALIASES.get(name, name))


def require_args(args: List[str], count: int, usage: str) -> None:
    if len(args) < count:
        raise UsageError(usage)


def get_contact(book: AddressBook, name: str) -> Record:
    record = book.find(name)
    if record is None:
        raise KeyError(
            f"Contact '{name}' not found. Use 'all' or 'find' to see contacts."
        )
    return record


def split_tags(words: List[str]) -> tuple:
    """Separate '#tag' words from the rest: returns (text, [tags])."""
    tags = [word for word in words if INLINE_TAG.match(word)]
    text = " ".join(word for word in words if not INLINE_TAG.match(word))
    return text, tags


def format_records(records: List[Record], empty: str) -> str:
    if not records:
        return empty
    return "\n\n".join(str(record) for record in records)


def format_notes(notes: List[Note], empty: str) -> str:
    if not notes:
        return empty
    return "\n".join(str(note) for note in notes)


# ---------------------------------------------------------------- contacts


@command(
    "add",
    "add <name> [phone]",
    "Create a contact (or add a phone to an existing one)",
    "Contacts",
    changes_data=True,
    aliases=("add-contact",),
)
def add_contact(args: List[str], ctx: Context) -> str:
    require_args(args, 1, "add <name> [phone]")
    name, *rest = args
    record = ctx.book.find(name)
    if record is None:
        record = Record(name)
        if rest:
            record.add_phone(rest[0])  # validated before the contact is saved
        ctx.book.add_record(record)
        return f"Contact '{record.name}' added."
    if not rest:
        return f"Contact '{record.name}' already exists."
    if not record.add_phone(rest[0]):
        return f"{record.name} already has this phone."
    return f"Phone added to '{record.name}'."


@command(
    "add-phone",
    "add-phone <name> <phone>",
    "Add a phone to a contact",
    "Contacts",
    changes_data=True,
)
def add_phone(args: List[str], ctx: Context) -> str:
    require_args(args, 2, "add-phone <name> <phone>")
    record = get_contact(ctx.book, args[0])
    if not record.add_phone(args[1]):
        return f"{record.name} already has this phone."
    return f"Phone added to '{record.name}'."


@command(
    "change-phone",
    "change-phone <name> <old phone> <new phone>",
    "Replace a phone",
    "Contacts",
    changes_data=True,
    aliases=("change",),
)
def change_phone(args: List[str], ctx: Context) -> str:
    require_args(args, 3, "change-phone <name> <old phone> <new phone>")
    record = get_contact(ctx.book, args[0])
    record.edit_phone(args[1], args[2])
    return f"Phone of '{record.name}' changed."


@command(
    "remove-phone",
    "remove-phone <name> <phone>",
    "Delete a phone from a contact",
    "Contacts",
    changes_data=True,
)
def remove_phone(args: List[str], ctx: Context) -> str:
    require_args(args, 2, "remove-phone <name> <phone>")
    record = get_contact(ctx.book, args[0])
    record.remove_phone(args[1])
    return f"Phone removed from '{record.name}'."


@command(
    "set-email",
    "set-email <name> <email>",
    "Set or change the email",
    "Contacts",
    changes_data=True,
    aliases=("add-email", "change-email"),
)
def set_email(args: List[str], ctx: Context) -> str:
    require_args(args, 2, "set-email <name> <email>")
    record = get_contact(ctx.book, args[0])
    record.set_email(args[1])
    return f"Email of '{record.name}' set to {record.email}."


@command(
    "remove-email",
    "remove-email <name>",
    "Delete the email",
    "Contacts",
    changes_data=True,
)
def remove_email(args: List[str], ctx: Context) -> str:
    require_args(args, 1, "remove-email <name>")
    record = get_contact(ctx.book, args[0])
    record.email = None
    return f"Email of '{record.name}' removed."


@command(
    "set-address",
    "set-address <name> <address...>",
    "Set or change the address",
    "Contacts",
    changes_data=True,
    aliases=("add-address", "change-address"),
)
def set_address(args: List[str], ctx: Context) -> str:
    require_args(args, 2, "set-address <name> <address...>")
    record = get_contact(ctx.book, args[0])
    record.set_address(" ".join(args[1:]))
    return f"Address of '{record.name}' set to: {record.address}."


@command(
    "remove-address",
    "remove-address <name>",
    "Delete the address",
    "Contacts",
    changes_data=True,
)
def remove_address(args: List[str], ctx: Context) -> str:
    require_args(args, 1, "remove-address <name>")
    record = get_contact(ctx.book, args[0])
    record.address = None
    return f"Address of '{record.name}' removed."


@command(
    "set-birthday",
    "set-birthday <name> <DD.MM.YYYY>",
    "Set or change the birthday",
    "Contacts",
    changes_data=True,
    aliases=("add-birthday", "change-birthday"),
)
def set_birthday(args: List[str], ctx: Context) -> str:
    require_args(args, 2, "set-birthday <name> <DD.MM.YYYY>")
    record = get_contact(ctx.book, args[0])
    record.set_birthday(args[1])
    return f"Birthday of '{record.name}' set to {record.birthday}."


@command(
    "remove-birthday",
    "remove-birthday <name>",
    "Delete the birthday",
    "Contacts",
    changes_data=True,
)
def remove_birthday(args: List[str], ctx: Context) -> str:
    require_args(args, 1, "remove-birthday <name>")
    record = get_contact(ctx.book, args[0])
    record.birthday = None
    return f"Birthday of '{record.name}' removed."


@command(
    "rename",
    "rename <name> <new name>",
    "Rename a contact",
    "Contacts",
    changes_data=True,
)
def rename_contact(args: List[str], ctx: Context) -> str:
    require_args(args, 2, "rename <name> <new name>")
    ctx.book.rename(args[0], args[1])
    return f"Contact '{args[0]}' renamed to '{args[1]}'."


@command(
    "delete",
    "delete <name>",
    "Delete a contact",
    "Contacts",
    changes_data=True,
    aliases=("delete-contact", "remove"),
)
def delete_contact(args: List[str], ctx: Context) -> str:
    require_args(args, 1, "delete <name>")
    record = ctx.book.delete(args[0])
    return f"Contact '{record.name}' deleted."


@command(
    "show",
    "show <name>",
    "Show all details of a contact",
    "Contacts",
    aliases=("show-contact",),
)
def show_contact(args: List[str], ctx: Context) -> str:
    require_args(args, 1, "show <name>")
    return str(get_contact(ctx.book, args[0]))


@command("phone", "phone <name>", "Show the phones of a contact", "Contacts")
def show_phone(args: List[str], ctx: Context) -> str:
    require_args(args, 1, "phone <name>")
    record = get_contact(ctx.book, args[0])
    if not record.phones:
        return f"{record.name} has no phones."
    return f"{record.name}: {', '.join(p.value for p in record.phones)}"


@command(
    "show-birthday",
    "show-birthday <name>",
    "Show the birthday of a contact",
    "Contacts",
)
def show_birthday(args: List[str], ctx: Context) -> str:
    require_args(args, 1, "show-birthday <name>")
    record = get_contact(ctx.book, args[0])
    if record.birthday is None:
        return f"{record.name} has no birthday saved."
    left = record.days_to_birthday()
    return f"{record.name}: {record.birthday} (in {left} days)"


@command("all", "all", "Show all contacts", "Contacts", aliases=("contacts",))
def show_all(args: List[str], ctx: Context) -> str:
    return format_records(
        ctx.book.sorted_records(),
        "The address book is empty. Add a contact with 'add <name>'.",
    )


@command(
    "find",
    "find <text>",
    "Search contacts by name, phone, email, address or birthday",
    "Contacts",
    aliases=("search", "find-contact"),
)
def find_contacts(args: List[str], ctx: Context) -> str:
    require_args(args, 1, "find <text>")
    query = " ".join(args)
    return format_records(
        ctx.book.search(query), f"No contacts match '{query}'."
    )


@command(
    "birthdays",
    "birthdays [days]",
    f"Birthdays in the next N days (default {DEFAULT_BIRTHDAY_DAYS})",
    "Contacts",
)
def birthdays(args: List[str], ctx: Context) -> str:
    days = DEFAULT_BIRTHDAY_DAYS
    if args:
        if not args[0].isdigit():
            raise ValueError(
                f"Number of days must be a whole number, got '{args[0]}'."
            )
        days = int(args[0])
    upcoming = ctx.book.upcoming_birthdays(days)
    if not upcoming:
        return f"No birthdays in the next {days} days."
    lines = [f"Birthdays in the next {days} days:"]
    for record, left in upcoming:
        when = (
            "today"
            if left == 0
            else "tomorrow" if left == 1 else f"in {left} days"
        )
        lines.append(
            f"  {record.name}: {record.birthday.value:%d.%m} ({when})"
        )
    return "\n".join(lines)


# ------------------------------------------------------------------- notes


@command(
    "add-note",
    "add-note <text...> [#tag ...]",
    "Add a note; words like #work become tags",
    "Notes",
    changes_data=True,
)
def add_note(args: List[str], ctx: Context) -> str:
    require_args(args, 1, "add-note <text...> [#tag ...]")
    text, tags = split_tags(args)
    note = ctx.notes.add(text, tags)
    return f"Note {note.id} added." + (
        f" Tags: {' '.join('#' + t for t in note.tag_names())}"
        if note.tags
        else ""
    )


@command("notes", "notes", "Show all notes", "Notes", aliases=("all-notes",))
def show_notes(args: List[str], ctx: Context) -> str:
    return format_notes(
        ctx.notes.all_notes(), "No notes yet. Add one with 'add-note <text>'."
    )


@command("show-note", "show-note <id>", "Show one note", "Notes")
def show_note(args: List[str], ctx: Context) -> str:
    require_args(args, 1, "show-note <id>")
    return str(ctx.notes.get_note(args[0]))


@command(
    "edit-note",
    "edit-note <id> <new text...> [#tag ...]",
    "Replace the text of a note (#words are added as tags)",
    "Notes",
    changes_data=True,
)
def edit_note(args: List[str], ctx: Context) -> str:
    require_args(args, 2, "edit-note <id> <new text...> [#tag ...]")
    note = ctx.notes.get_note(args[0])
    text, tags = split_tags(args[1:])
    for tag in tags:
        Tag(tag)  # validate everything before changing the note
    note.edit(text)
    note.add_tags(tags)
    return f"Note {note.id} updated."


@command(
    "delete-note",
    "delete-note <id>",
    "Delete a note",
    "Notes",
    changes_data=True,
    aliases=("remove-note",),
)
def delete_note(args: List[str], ctx: Context) -> str:
    require_args(args, 1, "delete-note <id>")
    note = ctx.notes.delete(args[0])
    return f"Note {note.id} deleted."


@command(
    "find-note",
    "find-note <text>",
    "Search notes by text and tags",
    "Notes",
    aliases=("search-note", "search-notes"),
)
def find_note(args: List[str], ctx: Context) -> str:
    require_args(args, 1, "find-note <text>")
    query = " ".join(args)
    return format_notes(ctx.notes.search(query), f"No notes match '{query}'.")


@command(
    "add-tag",
    "add-tag <id> <tag> [tag ...]",
    "Add tags to a note",
    "Notes",
    changes_data=True,
    aliases=("add-tags",),
)
def add_tag(args: List[str], ctx: Context) -> str:
    require_args(args, 2, "add-tag <id> <tag> [tag ...]")
    note = ctx.notes.get_note(args[0])
    added = note.add_tags(args[1:])
    if not added:
        return f"Note {note.id} already has these tags."
    added_text = " ".join("#" + tag.value for tag in added)
    return f"Tags added to note {note.id}: {added_text}"


@command(
    "remove-tag",
    "remove-tag <id> <tag>",
    "Remove a tag from a note",
    "Notes",
    changes_data=True,
)
def remove_tag(args: List[str], ctx: Context) -> str:
    require_args(args, 2, "remove-tag <id> <tag>")
    note = ctx.notes.get_note(args[0])
    note.remove_tag(args[1])
    return f"Tag removed from note {note.id}."


@command(
    "find-tag",
    "find-tag <tag> [tag ...]",
    "Notes that have all the given tags",
    "Notes",
    aliases=("find-tags", "search-tag"),
)
def find_tag(args: List[str], ctx: Context) -> str:
    require_args(args, 1, "find-tag <tag> [tag ...]")
    tags = " ".join("#" + Tag(tag).value for tag in args)
    return format_notes(ctx.notes.find_by_tags(args), f"No notes with {tags}.")


@command(
    "sort-notes",
    "sort-notes",
    "Show notes sorted by tags (untagged last)",
    "Notes",
    aliases=("sort-by-tag", "notes-by-tag"),
)
def sort_notes(args: List[str], ctx: Context) -> str:
    return format_notes(ctx.notes.sorted_by_tags(), "No notes yet.")


@command("tags", "tags", "List all tags with their notes", "Notes")
def show_tags(args: List[str], ctx: Context) -> str:
    groups = ctx.notes.group_by_tag()
    if not groups:
        return "No tags yet. Add one with 'add-tag <id> <tag>'."
    lines = []
    for tag, notes in groups.items():
        ids = ", ".join(str(note.id) for note in notes)
        lines.append(f"#{tag} ({len(notes)}): notes {ids}")
    return "\n".join(lines)


# ----------------------------------------------------------------- general


@command("hello", "hello", "Greeting", "General", aliases=("hi",))
def hello(args: List[str], ctx: Context) -> str:
    return "Hello! How can I help you? Type 'help' to see the commands."


@command(
    "help",
    "help [command]",
    "Show the commands or help for one command",
    "General",
    aliases=("?",),
)
def show_help(args: List[str], ctx: Context) -> str:
    if args:
        typed = args[0].lower()
        name = ALIASES.get(typed, typed)
        cmd = COMMANDS.get(name)
        if cmd is None:
            raise KeyError(f"Unknown command '{args[0]}'.")
        aliases = sorted(
            alias for alias, target in ALIASES.items() if target == name
        )
        alias_text = ", ".join(aliases) or "-"
        return f"{cmd.usage}\n    {cmd.description}\n    Aliases: {alias_text}"
    width = max(len(cmd.usage) for cmd in COMMANDS.values())
    lines = []
    for group in ("Contacts", "Notes", "General"):
        lines.append(f"{group}:")
        for cmd in COMMANDS.values():
            if cmd.group == group:
                lines.append(f"  {cmd.usage.ljust(width)}  {cmd.description}")
        lines.append("")
    lines.append(f"  {'exit / close / quit'.ljust(width)}  Save and exit")
    return "\n".join(lines)
