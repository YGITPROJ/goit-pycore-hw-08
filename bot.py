import re
from collections import UserDict
from datetime import datetime, date
import pickle

# ----------------------------------------------------------------------------

class Field:
    """
    Базовий клас для всіх полів
    """
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Birthday(Field):
    """
    Клас для зберігання дня народження
    """
    def __init__(self, value):
        try:
            parsed_date = datetime.strptime(value, "%d.%m.%Y").date()
            super().__init__(parsed_date)
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")

    def __str__(self):
        return self.value.strftime("%d.%m.%Y")


class Name(Field):
    """
    Клас для зберігання імені
    """
    pass


class Phone(Field):
    """
    Клас для зберігання номера телефону
    """
    def __init__(self, value):
        if not self.validate(value):
            raise ValueError("Invalid phone number: must be 10 digits.")
        super().__init__(value)

    @staticmethod
    def validate(phone_number: str) -> bool:
        """
        Статичний метод валідації номеру
        """
        return len(phone_number) == 10 and phone_number.isdigit()


class Record:
    """
    Клас для зберігання одного запису
    """
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone_number: str):
        self.phones.append(Phone(phone_number))

    def remove_phone(self, phone_number: str):
        phone_to_remove = self.find_phone(phone_number)
        if phone_to_remove:
            self.phones.remove(phone_to_remove)
        else:
            raise ValueError(f"Phone number {phone_number} not found.")

    def edit_phone(self, old_phone_number: str, new_phone_number: str):
        phone_to_edit = self.find_phone(old_phone_number)
        if phone_to_edit:
            new_phone = Phone(new_phone_number)
            index = self.phones.index(phone_to_edit)
            self.phones[index] = new_phone
        else:
            raise ValueError(f"Phone number {old_phone_number} not found.")

    def find_phone(self, phone_number: str):
        for phone in self.phones:
            if phone.value == phone_number:
                return phone
        return None

    def add_birthday(self, birthday_str: str):
        self.birthday = Birthday(birthday_str)

    def __str__(self):
        phone_list = "; ".join(p.value for p in self.phones)
        birthday_str = f", birthday: {self.birthday}" if self.birthday else ""
        return f"Contact name: {self.name.value}, phones: {phone_list}{birthday_str}"


class AddressBook(UserDict):
    """
    Клас для управління адресною книгою
    """
    def add_record(self, record: Record):
        self.data[record.name.value] = record

    def find(self, name: str) -> Record:
        return self.data.get(name)

    def delete(self, name: str):
        if name in self.data:
            del self.data[name]
        else:
            raise KeyError(f"Contact '{name}' not found.")

    def get_upcoming_birthdays(self) -> list:
        today = date.today()
        upcoming_birthdays = []
        for record in self.data.values():
            if not record.birthday:
                continue
            bday = record.birthday.value
            bday_this_year = bday.replace(year=today.year)
            if bday_this_year < today:
                bday_this_year = bday.replace(year=today.year + 1)
            delta_days = (bday_this_year - today).days
            if 0 <= delta_days <= 7:
                weekday = bday_this_year.weekday()
                if weekday >= 5:
                    day_to_congratulate = "Monday"
                else:
                    day_to_congratulate = bday_this_year.strftime("%A")
                upcoming_birthdays.append(
                    {
                        "name": record.name.value,
                        "congratulation_day": day_to_congratulate,
                    }
                )
        return upcoming_birthdays

# ----------------------------------------------------------------------------

def save_data(book, filename="addressbook.pkl"):
    """
    Зберігає адресну книгу у файл
    """
    with open(filename, "wb") as f:
        pickle.dump(book, f)

def load_data(filename="addressbook.pkl"):
    """
    Завантажує адресну книгу з файлу.
    Якщо файл не знайдено або пошкоджено, повертає нову, порожню книгу
    """
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except (FileNotFoundError, pickle.UnpicklingError, EOFError):
        return AddressBook()  

# ----------------------------------------------------------------------------

def input_error(func):
    """
    Декоратор, який обробляє помилки вводу
    """
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as e:
            return str(e)
        except (KeyError, AttributeError):
            return "Contact not found."
        except IndexError:
            return "Not enough arguments. Please provide full info."
    return inner

# ----------------------------------------------------------------------------

@input_error
def add_contact(args, book: AddressBook):
    name, phone, *_ = args
    record = book.find(name)
    message = "Contact updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    if phone:
        record.add_phone(phone)
    return message

@input_error
def change_contact(args, book: AddressBook):
    name, old_phone, new_phone = args
    record = book.find(name)
    record.edit_phone(old_phone, new_phone)
    return f"Contact '{name}' updated: {old_phone} -> {new_phone}."

@input_error
def show_phone(args, book: AddressBook):
    name = args[0]
    record = book.find(name)
    if record.phones:
        phone_list = '; '.join(p.value for p in record.phones)
        return f"{name}'s phones: {phone_list}"
    else:
        return f"Contact '{name}' exists but has no phones."

def show_all(book: AddressBook):
    if not book.data:
        return "No contacts found."
    return "\n".join(str(record) for record in book.data.values())

@input_error
def add_birthday(args, book: AddressBook):
    name, bday_str = args
    record = book.find(name)
    record.add_birthday(bday_str)
    return "Birthday added."

@input_error
def show_birthday(args, book: AddressBook):
    name = args[0]
    record = book.find(name)
    if record.birthday:
        return str(record.birthday)
    else:
        return "Birthday not set for this contact."

@input_error
def birthdays(args, book: AddressBook):
    upcoming = book.get_upcoming_birthdays()
    if not upcoming:
        return "No upcoming birthdays in the next week."
    response = "Upcoming birthdays:\n"
    for item in upcoming:
        response += f"  {item['name']}: {item['congratulation_day']}\n"
    return response.strip()

# ----------------------------------------------------------------------------

def parse_input(user_input):
    """
    Парсер команд
    """
    parts = user_input.split()
    if not parts:
        return None, []
    cmd = parts[0].strip().lower()
    args = parts[1:]
    return cmd, args


def main():
    """
    Головний цикл бота
    """
    # ЗАВАНТАЖИТИ
    book = load_data() 
    print("Welcome to the assistant bot!")
    if book.data:
        print(f"Loaded {len(book.data)} contacts from file.")

    while True:
        user_input = input("Enter a command: ")

        parsed_data = parse_input(user_input)
        if not parsed_data[0]:
            print("Invalid command. Please try again.")
            continue

        command, args = parsed_data

        if command in ["close", "exit"]:
            # ЗБЕРЕГТИ
            save_data(book)
            print("Good bye!")
            break

        elif command == "hello":
            print("How can I help you?")

        elif command == "add":
            print(add_contact(args, book))

        elif command == "change":
            print(change_contact(args, book))

        elif command == "phone":
            print(show_phone(args, book))

        elif command == "all":
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