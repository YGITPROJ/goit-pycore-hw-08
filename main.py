#
#
#
from bot import main as bot


#
#
#
def main():

    while True:
        print("\n--- Головне меню Домашнього Завдання ---")
        print("Оберіть завдання для запуску:")
        print("1. БОТ-Асистент")
        print("0. Вихід")

        choice = input("Ваш вибір (0-4): ").strip()

        match choice:
            case "1":
                print("\n[ 1. БОТ-Асисен ]")
                print("-" * 30)
                try:
                    bot()
                except Exception as e:
                    print(f"Сталася критична помилка: {e}")
                print("-" * 30)
                input("Натисніть Enter, щоб повернутись у меню...")

            case "0":
                print("\n--- Роботу завершено. До побачення! ---")
                break
            case _:
                print("\nНеправильний вибір. Будь ласка, введіть число від 0 до 4.")
                input("Натисніть Enter, щоб спробувати ще раз...")


if __name__ == "__main__":
    main()
