"""Tests for the Personal Assistant.

Run with: python -m unittest discover -s tests
"""

import io
import os
import tempfile
import unittest
from contextlib import redirect_stdout
from datetime import date, timedelta
from unittest import mock

from personal_assistant import storage
from personal_assistant.commands import Context
from personal_assistant.contacts import AddressBook, Record
from personal_assistant.fields import (
    Address,
    Birthday,
    Email,
    Name,
    NoteText,
    Phone,
    Tag,
)
from personal_assistant.main import handle, main, parse_input
from personal_assistant.notes import NoteBook


class FieldValidationTest(unittest.TestCase):
    def test_phone_accepts_ten_digits_with_separators(self):
        self.assertEqual(Phone("(050) 123-45-67").value, "0501234567")

    def test_phone_rejects_wrong_length_and_letters(self):
        for bad in ["123", "05012345678", "05012345ab", ""]:
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                Phone(bad)

    def test_email(self):
        self.assertEqual(
            Email("Anna.K@Example.com").value, "anna.k@example.com"
        )
        for bad in ["anna", "anna@", "@x.com", "anna@x", "an na@x.com"]:
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                Email(bad)

    def test_birthday(self):
        self.assertEqual(str(Birthday("15.05.1990")), "15.05.1990")
        future = (date.today() + timedelta(days=1)).strftime("%d.%m.%Y")
        for bad in ["1990-05-15", "31.02.1990", future]:
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                Birthday(bad)

    def test_name_address_note_tag(self):
        with self.assertRaises(ValueError):
            Name("  ")
        with self.assertRaises(ValueError):
            Name("x" * 51)
        self.assertEqual(
            Address("  Kyiv,   Main st 1 ").value, "Kyiv, Main st 1"
        )
        with self.assertRaises(ValueError):
            NoteText("")
        self.assertEqual(Tag("#Work").value, "work")
        with self.assertRaises(ValueError):
            Tag("two words")


class AddressBookTest(unittest.TestCase):
    def setUp(self):
        self.book = AddressBook()
        anna = Record("Anna")
        anna.add_phone("0501234567")
        anna.set_email("anna@example.com")
        anna.set_address("Kyiv, Khreshchatyk 1")
        self.book.add_record(anna)
        self.book.add_record(Record("Bob"))

    def test_find_is_case_insensitive_and_duplicates_rejected(self):
        self.assertIs(self.book.find("anna"), self.book.find("Anna"))
        with self.assertRaises(ValueError):
            self.book.add_record(Record("ANNA"))

    def test_search_by_any_field(self):
        for query in ["ann", "050-123", "example.com", "kyiv"]:
            with self.subTest(query=query):
                self.assertEqual(
                    [r.name.value for r in self.book.search(query)], ["Anna"]
                )
        self.assertEqual(self.book.search("nothing"), [])

    def test_edit_and_remove_phone(self):
        anna = self.book.find("Anna")
        anna.edit_phone("0501234567", "0671112233")
        self.assertEqual([p.value for p in anna.phones], ["0671112233"])
        with self.assertRaises(ValueError):
            anna.edit_phone("0000000000", "0671112233")
        anna.remove_phone("0671112233")
        self.assertEqual(anna.phones, [])

    def test_rename_and_delete(self):
        self.book.rename("bob", "Robert")
        self.assertIsNone(self.book.find("Bob"))
        self.assertIsNotNone(self.book.find("Robert"))
        with self.assertRaises(ValueError):
            self.book.rename("Robert", "anna")
        self.book.delete("Robert")
        with self.assertRaises(KeyError):
            self.book.delete("Robert")

    def test_upcoming_birthdays(self):
        today = date(2026, 3, 10)
        self.book.find("Anna").set_birthday("12.03.1990")  # in 2 days
        self.book.find("Bob").set_birthday("10.04.1985")  # in 31 days
        self.assertEqual(
            [
                (r.name.value, d)
                for r, d in self.book.upcoming_birthdays(7, today)
            ],
            [("Anna", 2)],
        )
        self.assertEqual(len(self.book.upcoming_birthdays(31, today)), 2)
        self.assertEqual(self.book.upcoming_birthdays(1, today), [])

    def test_birthday_wraps_to_next_year_and_leap_day(self):
        record = Record("Leap")
        record.set_birthday("29.02.2000")
        self.assertEqual(
            record.days_to_birthday(date(2027, 2, 27)), 2
        )  # 1 March in a non-leap year
        record.set_birthday("01.01.2000")
        self.assertEqual(record.days_to_birthday(date(2026, 12, 31)), 1)


class NoteBookTest(unittest.TestCase):
    def setUp(self):
        self.notes = NoteBook()
        self.notes.add("Buy milk", ["shopping"])
        self.notes.add("Prepare the demo", ["work", "python"])
        self.notes.add("Read a book")

    def test_ids_are_not_reused(self):
        self.notes.delete(3)
        self.assertEqual(self.notes.add("New").id, 4)

    def test_search_text_and_tags(self):
        self.assertEqual([n.id for n in self.notes.search("DEMO")], [2])
        self.assertEqual([n.id for n in self.notes.search("#shop")], [1])

    def test_edit_tags_and_find_by_tags(self):
        self.notes.get_note("1").edit("Buy oat milk")
        self.assertEqual(self.notes.get_note(1).text.value, "Buy oat milk")
        self.notes.get_note(3).add_tags(["#Python"])
        self.assertEqual(
            [n.id for n in self.notes.find_by_tags(["python"])], [2, 3]
        )
        self.assertEqual(
            [n.id for n in self.notes.find_by_tags(["python", "work"])], [2]
        )
        self.notes.get_note(3).remove_tag("python")
        self.assertEqual(
            [n.id for n in self.notes.find_by_tags(["python"])], [2]
        )

    def test_sort_and_group_by_tags(self):
        self.assertEqual(
            [n.id for n in self.notes.sorted_by_tags()], [2, 1, 3]
        )  # python < shopping, untagged last
        self.assertEqual(
            list(self.notes.group_by_tag()), ["python", "shopping", "work"]
        )

    def test_bad_ids(self):
        with self.assertRaises(ValueError):
            self.notes.get_note("abc")
        with self.assertRaises(KeyError):
            self.notes.get_note(99)


class TempDataDirTest(unittest.TestCase):
    """Base class: keeps the data in a temporary folder."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        patcher = mock.patch.dict(
            os.environ, {"PERSONAL_ASSISTANT_HOME": self.tmp.name}
        )
        patcher.start()
        self.addCleanup(patcher.stop)
        self.addCleanup(self.tmp.cleanup)

    def run_session(self, *lines):
        """Run the real main() with these input lines; return the output."""
        out = io.StringIO()
        with mock.patch(
            "builtins.input", side_effect=list(lines) + [EOFError()]
        ), redirect_stdout(out):
            main()
        return out.getvalue()


class StorageTest(TempDataDirTest):
    def test_round_trip(self):
        book, notes = AddressBook(), NoteBook()
        book.add_record(Record("Anna"))
        notes.add("Hello", ["x"])
        storage.save_all(book, notes)
        self.assertIn("Anna", storage.load_contacts())
        self.assertEqual(storage.load_notes().get_note(1).tag_names(), ["x"])
        self.assertEqual(storage.load_notes().next_id, 2)

    def test_missing_file_gives_empty_book(self):
        self.assertEqual(len(storage.load_contacts()), 0)

    def test_damaged_file_is_kept_as_backup(self):
        path = storage.data_dir() / storage.CONTACTS_FILE
        path.write_bytes(b"garbage")
        with redirect_stdout(io.StringIO()):
            self.assertEqual(len(storage.load_contacts()), 0)
        self.assertTrue(path.with_name(path.name + ".bak").exists())


class CliTest(TempDataDirTest):
    def ctx(self):
        return Context(AddressBook(), NoteBook())

    def test_parse_input(self):
        self.assertEqual(
            parse_input('ADD "Anna Maria" 050'), ("add", ["Anna Maria", "050"])
        )
        self.assertEqual(parse_input("add O'Neil"), ("add", ["O'Neil"]))
        self.assertEqual(parse_input("   "), ("", []))

    def test_bad_input_never_raises(self):
        ctx = self.ctx()
        for line in [
            "add",
            "add Anna 123",
            "phone Nobody",
            "set-email",
            "birthdays x",
            "edit-note 1",
            "delete-note abc",
            "find-tag",
            "add-tag 5 work",
            "help nope",
            "set-birthday Nobody 01.01.2000",
            "addd Anna",
        ]:
            with self.subTest(line=line):
                output, _ = handle(line, ctx)
                self.assertTrue(output)

    def test_typo_suggestion(self):
        self.assertIn("add-note", handle("add-nte x", self.ctx())[0])

    def test_inline_tags(self):
        ctx = self.ctx()
        handle("add-note Call the bank #finance #todo", ctx)
        note = ctx.notes.get_note(1)
        self.assertEqual(note.text.value, "Call the bank")
        self.assertEqual(note.tag_names(), ["finance", "todo"])

    def test_data_survives_restart(self):
        self.run_session(
            "add Anna 0501234567",
            "set-email Anna anna@example.com",
            "set-address Anna Kyiv, Khreshchatyk 1",
            "set-birthday Anna 15.05.1990",
            "add-note Prepare slides #work",
            "exit",
        )
        output = self.run_session("show Anna", "notes")
        self.assertIn("anna@example.com", output)
        self.assertIn("Kyiv, Khreshchatyk 1", output)
        self.assertIn("15.05.1990", output)
        self.assertIn("Prepare slides", output)
        self.assertIn("#work", output)

    def test_data_saved_after_each_change(self):
        # A crash after the first command: the change is already on disk
        out = io.StringIO()
        with mock.patch(
            "builtins.input", side_effect=["add Anna", RuntimeError("crash")]
        ), redirect_stdout(out), mock.patch.object(
            storage, "save_all", wraps=storage.save_all
        ) as saver:
            with self.assertRaises(RuntimeError):
                main()
        self.assertGreaterEqual(saver.call_count, 1)
        self.assertIn("Anna", storage.load_contacts())


if __name__ == "__main__":
    unittest.main()
