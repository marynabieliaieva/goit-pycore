"""Notes with tags and the ``NoteBook`` that holds them."""

from collections import UserDict
from datetime import datetime
from typing import Dict, Iterable, List

from .fields import NoteText, Tag


class Note:
    """A text note with an id, a creation time and a set of tags."""

    def __init__(self, note_id: int, text: str, tags: Iterable[str] = ()):
        self.id = note_id
        self.text = NoteText(text)
        self.tags: List[Tag] = []
        self.created = datetime.now()
        self.updated = self.created
        self.add_tags(tags)

    def edit(self, text: str) -> None:
        self.text = NoteText(text)
        self.updated = datetime.now()

    def add_tags(self, tags: Iterable[str]) -> List[Tag]:
        """Add tags the note does not have yet. Returns the ones added."""
        new_tags = [Tag(tag) for tag in tags]  # validate all before adding any
        added = []
        for tag in new_tags:
            if tag not in self.tags:
                self.tags.append(tag)
                added.append(tag)
        self.tags.sort(key=lambda t: t.value)
        return added

    def remove_tag(self, tag: str) -> None:
        item = Tag(tag)
        if item not in self.tags:
            raise ValueError(f"Note {self.id} has no tag #{item}.")
        self.tags.remove(item)

    def has_tag(self, tag: str) -> bool:
        return Tag(tag) in self.tags

    def tag_names(self) -> List[str]:
        return [tag.value for tag in self.tags]

    def __str__(self) -> str:
        tags = " ".join(f"#{tag}" for tag in self.tags)
        header = f"[{self.id}] {self.updated:%d.%m.%Y %H:%M}"
        if tags:
            header += f"  {tags}"
        return f"{header}\n    {self.text}"


class NoteBook(UserDict):
    """All notes, stored by numeric id. Ids are never reused."""

    def __init__(self):
        super().__init__()
        self.next_id = 1

    def add(self, text: str, tags: Iterable[str] = ()) -> Note:
        note = Note(self.next_id, text, tags)
        self.data[note.id] = note
        self.next_id += 1
        return note

    def get_note(self, note_id) -> Note:
        """Return the note by id (``note_id`` may be a string)."""
        try:
            key = int(note_id)
        except (TypeError, ValueError):
            raise ValueError(
                f"Note id must be a number, got '{note_id}'."
            ) from None
        if key not in self.data:
            raise KeyError(f"Note {key} not found.")
        return self.data[key]

    def delete(self, note_id) -> Note:
        note = self.get_note(note_id)
        return self.data.pop(note.id)

    def all_notes(self) -> List[Note]:
        return sorted(self.data.values(), key=lambda n: n.id)

    def search(self, query: str) -> List[Note]:
        """Notes whose text or tags contain ``query`` (case-insensitive)."""
        query = query.strip().lower().lstrip("#")
        if not query:
            return []
        return [
            note
            for note in self.all_notes()
            if query in note.text.value.lower()
            or any(query in tag for tag in note.tag_names())
        ]

    def find_by_tags(self, tags: Iterable[str]) -> List[Note]:
        """Notes that have every one of ``tags``."""
        wanted = [Tag(tag) for tag in tags]
        return [
            note
            for note in self.all_notes()
            if all(tag in note.tags for tag in wanted)
        ]

    def sorted_by_tags(self) -> List[Note]:
        """Notes sorted by their tags alphabetically; untagged notes last."""
        return sorted(
            self.data.values(), key=lambda n: (not n.tags, n.tag_names(), n.id)
        )

    def group_by_tag(self) -> Dict[str, List[Note]]:
        """{tag: notes with this tag}, tags in alphabetical order."""
        groups: Dict[str, List[Note]] = {}
        for note in self.all_notes():
            for tag in note.tag_names():
                groups.setdefault(tag, []).append(note)
        return dict(sorted(groups.items()))
