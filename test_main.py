
from datetime import date

from main import (
    AddressBook,
    Birthday,
    Phone,
    Record,
    add_birthday,
    add_contact,
    change_contact,
    show_birthday,
    show_phone,
)


def test_address_book():
    book = AddressBook()

    assert add_contact(
        ["John", "1234567890"], book
    ) == "Contact added."

    assert add_contact(
        ["John", "5555555555"], book
    ) == "Contact updated."

    assert len(book.find("John").phones) == 2

    assert show_phone(
        ["John"], book
    ) == "1234567890; 5555555555"

    assert change_contact(
        ["John", "1234567890", "1112223333"], book
    ) == "Contact updated."

    assert book.find("John").find_phone(
        "1112223333"
    ) is not None

    assert add_birthday(
        ["John", "15.05.1990"], book
    ) == "Birthday added."

    assert show_birthday(
        ["John"], book
    ) == "15.05.1990"

    assert show_phone(
        ["Unknown"], book
    ) == "Contact not found."

    book.delete("John")
    assert book.find("John") is None


def test_validation():
    for number in ("12345", "12345678901", "abcdefghij"):
        try:
            Phone(number)
            raise AssertionError("Invalid phone accepted")
        except ValueError:
            pass

    for value in ("31.02.1990", "1990-05-15", "1.5.1990"):
        try:
            Birthday(value)
            raise AssertionError("Invalid birthday accepted")
        except ValueError:
            pass


def test_upcoming_birthdays():
    book = AddressBook()

    alex = Record("Alex")
    alex.add_birthday("15.11.1990")
    book.add_record(alex)

    maria = Record("Maria")
    maria.add_birthday("18.11.2000")
    book.add_record(maria)

    result = book.get_upcoming_birthdays(
        date(2026, 11, 12)
    )

    assert result == [
        {
            "name": "Alex",
            "congratulation_date": "2026-11-16"
        },
        {
            "name": "Maria",
            "congratulation_date": "2026-11-18"
        }
    ]

    # Weekend birthday carried into Monday
    monday_result = book.get_upcoming_birthdays(
        date(2026, 11, 16)
    )

    assert any(
        item["name"] == "Alex"
        for item in monday_result
    )


if __name__ == "__main__":
    test_address_book()
    test_validation()
    test_upcoming_birthdays()

    print("All tests passed!")
