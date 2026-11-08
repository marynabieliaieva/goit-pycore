"""Entry point: the command loop of the Personal Assistant."""

import difflib
import shlex
from typing import List, Tuple

from . import storage
from .commands import ALIASES, COMMANDS, Context, resolve

EXIT_COMMANDS = {"exit", "close", "quit", "bye"}
PROMPT = ">>> "


def parse_input(user_input: str) -> Tuple[str, List[str]]:
    """Split input into a lowercase command and its arguments.

    Quotes group words, so ``add "Anna Maria" 0501234567`` keeps the name
    together. If the quotes are unbalanced (for example a name like O'Neil),
    the input is simply split on spaces.
    """
    try:
        parts = shlex.split(user_input)
    except ValueError:
        parts = user_input.split()
    if not parts:
        return "", []
    return parts[0].lower(), parts[1:]


def suggest(command: str) -> str:
    """'Did you mean ...?' hint for a mistyped command."""
    names = list(COMMANDS) + list(ALIASES) + sorted(EXIT_COMMANDS)
    matches = difflib.get_close_matches(command, names, n=3, cutoff=0.6)
    if matches:
        return (
            f"Unknown command '{command}'. Did you mean: {', '.join(matches)}?"
        )
    return f"Unknown command '{command}'. Type 'help' to see all commands."


def handle(user_input: str, ctx: Context) -> Tuple[str, bool]:
    """Run one line of input. Returns (text to print, whether data changed)."""
    command, args = parse_input(user_input)
    if not command:
        return "", False
    cmd = resolve(command)
    if cmd is None:
        return suggest(command), False
    return cmd.handler(args, ctx), cmd.changes_data


def run(ctx: Context) -> None:
    """Ask for commands until the user exits; save after every change."""
    print(
        "Welcome to your Personal Assistant! Type 'help' to see the commands."
    )
    while True:
        try:
            user_input = input(PROMPT)
        except (EOFError, KeyboardInterrupt):
            print("\nGood bye!")
            return
        if parse_input(user_input)[0] in EXIT_COMMANDS:
            print("Good bye!")
            return
        output, changed = handle(user_input, ctx)
        if output:
            print(output)
        if changed:
            storage.save_all(ctx.book, ctx.notes)


def main() -> None:
    ctx = Context(storage.load_contacts(), storage.load_notes())
    try:
        run(ctx)
    finally:
        # Also covers Ctrl+C, end of input and unexpected errors
        storage.save_all(ctx.book, ctx.notes)


if __name__ == "__main__":
    main()
