from pathlib import Path
from pprint import pprint
from typing import Dict, List, Union


def get_cats_info(path: Union[str, Path]) -> List[Dict[str, str]]:
    """Return a list of cats from an 'id,name,age' file.

    Malformed lines are skipped with a warning. If the file is missing or
    unreadable, returns an empty list.
    """
    cats = []
    try:
        with open(path, "r", encoding="utf-8") as file:
            for line_number, line in enumerate(file, start=1):
                line = line.strip()
                if not line:
                    continue
                try:
                    cat_id, name, age = line.split(",")
                except ValueError:
                    print(f"Skipping malformed line {line_number}: '{line}'")
                    continue
                cats.append({"id": cat_id, "name": name, "age": age})
    except FileNotFoundError:
        print(f"File not found: {path}")
    except (OSError, UnicodeDecodeError) as error:
        print(f"Cannot read file {path}: {error}")
    return cats


if __name__ == "__main__":
    cats_file = Path(__file__).parent / "data" / "cats_file.txt"
    cats_info = get_cats_info(cats_file)
    pprint(cats_info, sort_dicts=False)
