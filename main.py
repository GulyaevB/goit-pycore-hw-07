
from collections import UserDict
from datetime import date, datetime, timedelta
from functools import wraps


class Field:
    """Base class for contact fields."""

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Name(Field):
    """Contact name. This field is required."""

    def __init__(self, value):
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Contact name cannot be empty")

        super().__init__(value)


class Phone(Field):
    """Phone number containing exactly 10 digits."""

    def __init__(self, value):
        if (
            not isinstance(value, str)
            or len(value) != 10
            or not value.isascii()
            or not value.isdigit()
        ):
            raise ValueError("Phone number must contain 10 digits")

        super().__init__(value)


class Birthday(Field):
    """Birthday stored as a datetime object."""

    def __init__(self, value):
        try:
            birthday = datetime.strptime(value, "%d.%m.%Y")

            if birthday.strftime("%d.%m.%Y") != value:
                raise ValueError

        except (ValueError, TypeError):
            raise ValueError(
                "Invalid date format. Use DD.MM.YYYY"
            )

        super().__init__(birthday)

    def __str__(self):
        return self.value.strftime("%d.%m.%Y")


class Record:
    """Contact record with phones and an optional birthday."""

    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone):
        """Add a validated phone number."""
        self.phones.append(Phone(phone))

    def find_phone(self, phone):
        """Return the matching Phone object or None."""
        for item in self.phones:
            if item.value == phone:
                return item

        return None

    def edit_phone(self, old_phone, new_phone):
        """Replace a phone number after validation."""
        phone = self.find_phone(old_phone)

        if phone is None:
            raise ValueError("Phone number not found")

        validated = Phone(new_phone)
        phone.value = validated.value

    def remove_phone(self, phone):
        """Remove a phone number if it exists."""
        found = self.find_phone(phone)

        if found is not None:
            self.phones.remove(found)

    def add_birthday(self, birthday):
        """Set or update the contact's birthday."""
        self.birthday = Birthday(birthday)

    def __str__(self):
        phones = "; ".join(phone.value for phone in self.phones)

        if not phones:
            phones = "No phones"

        return f"Contact name: {self.name.value}, phones: {phones}"


class AddressBook(UserDict):
    """Address book containing contact records."""

    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)

    def delete(self, name):
        self.data.pop(name, None)

    def get_upcoming_birthdays(self, today=None):
        """Return greetings scheduled within the next 7 days."""
        if today is None:
            today = date.today()

        end_date = today + timedelta(days=7)
        upcoming = []

        for record in self.data.values():
            if record.birthday is None:
                continue

            birthday = record.birthday.value.date()

            # Check nearby years for year-boundary cases
            for year in (today.year - 1, today.year, today.year + 1):
                if year < birthday.year:
                    continue

                try:
                    celebration = birthday.replace(year=year)
                except ValueError:
                    # February 29 in a non-leap year
                    celebration = date(year, 2, 28)

                # Saturday or Sunday -> next Monday
                if celebration.weekday() == 5:
                    celebration += timedelta(days=2)
                elif celebration.weekday() == 6:
                    celebration += timedelta(days=1)

                if today <= celebration <= end_date:
                    upcoming.append({
                        "name": record.name.value,
                        "congratulation_date": celebration.strftime(
                            "%Y-%m-%d"
                        )
                    })
                    break

        upcoming.sort(
            key=lambda item: (
                item["congratulation_date"],
                item["name"]
            )
        )

        return upcoming


def input_error(func):
    """Convert input-related exceptions into user messages."""

    @wraps(func)
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)

        except ValueError as error:
            return str(error)

        except IndexError:
            return "Enter the required arguments."

        except KeyError:
            return "Contact not found."

    return inner


def parse_input(user_input):
    """Split CLI input into a command and its arguments."""
    parts = user_input.strip().split()

    if not parts:
        return "", []

    return parts[0].lower(), parts[1:]


@input_error
def add_contact(args, book):
    if len(args) != 2:
        raise ValueError("Give me name and phone please.")

    name, phone = args
    Phone(phone)

    record = book.find(name)

    if record is None:
        record = Record(name)
        record.add_phone(phone)
        book.add_record(record)
        return "Contact added."

    record.add_phone(phone)
    return "Contact updated."


@input_error
def change_contact(args, book):
    if len(args) != 3:
        raise ValueError("Give me name, old phone and new phone.")

    name, old_phone, new_phone = args
    record = book.find(name)

    if record is None:
        return "Contact not found."

    record.edit_phone(old_phone, new_phone)
    return "Contact updated."


@input_error
def show_phone(args, book):
    if len(args) != 1:
        raise ValueError("Enter user name.")

    record = book.find(args[0])

    if record is None:
        return "Contact not found."

    if not record.phones:
        return "No phones found."

    return "; ".join(phone.value for phone in record.phones)


@input_error
def show_all(book):
    if not book.data:
        return "No contacts found."

    return "\n".join(
        str(record) for record in book.data.values()
    )


@input_error
def add_birthday(args, book):
    if len(args) != 2:
        raise ValueError("Give me name and birthday please.")

    name, birthday = args
    record = book.find(name)

    if record is None:
        return "Contact not found."

    record.add_birthday(birthday)
    return "Birthday added."


@input_error
def show_birthday(args, book):
    if len(args) != 1:
        raise ValueError("Enter user name.")

    record = book.find(args[0])

    if record is None:
        return "Contact not found."

    if record.birthday is None:
        return "Birthday not set."

    return str(record.birthday)


@input_error
def birthdays(args, book):
    if args:
        raise ValueError(
            "The birthdays command takes no arguments."
        )

    upcoming = book.get_upcoming_birthdays()

    if not upcoming:
        return "No upcoming birthdays."

    result = []

    for item in upcoming:
        result.append(
            f"{item['name']}: {item['congratulation_date']}"
        )

    return "\n".join(result)


def main():
    """Run the command-line assistant."""
    book = AddressBook()

    print("Welcome to the assistant bot!")

    while True:
        try:
            user_input = input("Enter a command: ")

        except (EOFError, KeyboardInterrupt):
            print("\nGood bye!")
            break

        command, args = parse_input(user_input)

        if command in ("close", "exit") and not args:
            print("Good bye!")
            break

        elif command == "hello" and not args:
            print("How can I help you?")

        elif command == "add":
            print(add_contact(args, book))

        elif command == "change":
            print(change_contact(args, book))

        elif command == "phone":
            print(show_phone(args, book))

        elif command == "all" and not args:
            print(show_all(book))

        elif command == "add-birthday":
            print(add_birthday(args, book))

        elif command == "show-birthday":
            print(show_birthday(args, book))

        elif command == "birthdays":
            print(birthdays(args, book))

        else:
            print("Invalid command.")


if __name__ == "__main__":
    main()
