
from collections import UserDict
from functools import wraps


class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Name(Field):
    pass


class Phone(Field):
    def __init__(self, value):
        if (
            not isinstance(value, str)
            or len(value) != 10
            or not value.isascii()
            or not value.isdigit()
        ):
            raise ValueError("Phone number must contain 10 digits")

        super().__init__(value)


class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def find_phone(self, phone):
        for item in self.phones:
            if item.value == phone:
                return item
        return None

    def edit_phone(self, old_phone, new_phone):
        phone = self.find_phone(old_phone)
        if phone is None:
            raise ValueError("Phone number not found")

        validated = Phone(new_phone)
        phone.value = validated.value

    def remove_phone(self, phone):
        found = self.find_phone(phone)
        if found is not None:
            self.phones.remove(found)

    def __str__(self):
        phones = "; ".join(p.value for p in self.phones)
        return f"Contact name: {self.name.value}, phones: {phones}"


class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)

    def delete(self, name):
        self.data.pop(name, None)


def input_error(func):
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
    parts = user_input.strip().split()
    if not parts:
        return "", []
    return parts[0].lower(), parts[1:]


@input_error
def add_contact(args, book):
    if len(args) != 2:
        raise ValueError("Give me name and phone please.")

    name, phone = args

    # Validate before creating or updating the contact
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

    return "; ".join(phone.value for phone in record.phones)


@input_error
def show_all(book):
    if not book.data:
        return "No contacts found."

    return "\n".join(str(record) for record in book.data.values())


def main():
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
        else:
            print("Invalid command.")


if __name__ == "__main__":
    main()
