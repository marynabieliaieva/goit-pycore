import sys
from pathlib import Path

from colorama import Fore, Style, init

DIR_COLOR = Fore.BLUE + Style.BRIGHT
FILE_COLOR = Fore.GREEN


def print_tree(directory: Path, prefix: str = "") -> None:
    """Recursively print the contents of a directory as a tree."""
    try:
        # Directories first, then files, both alphabetically
        entries = sorted(directory.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower()))
    except PermissionError:
        print(f"{prefix}┗ {Fore.RED}[access denied]{Style.RESET_ALL}")
        return

    for index, entry in enumerate(entries):
        is_last = index == len(entries) - 1
        connector = "┗ " if is_last else "┣ "
        if entry.is_dir():
            print(f"{prefix}{connector}{DIR_COLOR}📂 {entry.name}{Style.RESET_ALL}")
            print_tree(entry, prefix + ("  " if is_last else "┃ "))
        else:
            print(f"{prefix}{connector}{FILE_COLOR}📜 {entry.name}{Style.RESET_ALL}")


def main() -> None:
    init(autoreset=True)

    if len(sys.argv) != 2:
        print(f"{Fore.YELLOW}Usage: python {Path(__file__).name} <path/to/directory>")
        sys.exit(1)

    directory = Path(sys.argv[1])
    if not directory.exists():
        print(f"{Fore.RED}Error: path '{directory}' does not exist.")
        sys.exit(1)
    if not directory.is_dir():
        print(f"{Fore.RED}Error: '{directory}' is not a directory.")
        sys.exit(1)

    print(f"{DIR_COLOR}📦 {directory.resolve().name}{Style.RESET_ALL}")
    print_tree(directory)


if __name__ == "__main__":
    main()
