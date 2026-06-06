import os
import webbrowser

from colorama import *
from pystyle import *

from menu import (
    banner,
    cleaner_menu,
    print_header,
    print_menu_item,
    print_separator,
    proxy_manager_menu,
    session_account_info_menu,
    session_analyzer_menu,
    session_creator_code_menu,
    session_creator_qr_menu,
    session_to_tdata_menu,
    tdata_to_session_menu,
)


os.system("clear" if os.name == "posix" else "cls")


def main_menu():
    os.system("clear" if os.name == "posix" else "cls")
    print(Colorate.Diagonal(Colors.blue_to_cyan, banner))
    print_separator()

    print_header("ОПЕРАЦИИ С СЕССИЯМИ")
    print_menu_item("01", "Анализ сессии", "Анализ аккаунта Telegram по .session")
    print_menu_item("02", "Создать session через QR", "Сканирование QR-кода")
    print_menu_item("03", "Создать session через код", "Авторизация по коду")

    print_header("КОНВЕРТАЦИЯ")
    print_menu_item("04", "Session --> Tdata", "Конвертация в формат Desktop")
    print_menu_item("05", "Tdata --> Session", "Конвертация в формат Telethon")
    print_menu_item("06", "Session --> Info", "Извлечение данных из .session в JSON")

    print_header("УПРАВЛЕНИЕ")
    print_menu_item("07", "Очистка каналов", "Массовый выход из каналов")
    print_menu_item("08", "Очистка групп", "Массовый выход из групп")
    print_menu_item("09", "Удаление ботов", "Блокировка всех ботов")
    print_menu_item("10", "Очистка диалогов", "Удаление личных чатов")

    print_header("СИСТЕМА")
    print_menu_item("11", "Контакты разработчиков", "Контакты оригинала и автора форка")
    print_menu_item("12", "Документация", "Открыть страницу проекта")
    print_menu_item("13", "Proxy Manager", "Прокси, ротация и планы распределения")
    print_menu_item("14", "Выход", "Завершение работы")

    print_separator()
    Write.Print("\n    > Выберите пункт меню: ", Colors.cyan_to_blue, interval=0.0005)
    return input().strip()


while True:
    choice = main_menu()

    if choice in ("01", "1"):
        session_account_info_menu()
    elif choice in ("02", "2"):
        session_creator_qr_menu()
    elif choice in ("03", "3"):
        session_creator_code_menu()
    elif choice in ("04", "4"):
        session_to_tdata_menu()
    elif choice in ("05", "5"):
        tdata_to_session_menu()
    elif choice in ("06", "6"):
        session_analyzer_menu()
    elif choice in ("07", "7"):
        cleaner_menu("channel")
    elif choice in ("08", "8"):
        cleaner_menu("chat")
    elif choice in ("09", "9"):
        cleaner_menu("bot")
    elif choice == "10":
        cleaner_menu("user")
    elif choice == "11":
        Write.Print("\n    [+] Разработчик форка:\n", Colors.cyan_to_blue, interval=0.0005)
        Write.Print("\n    • Telegram: ", Colors.cyan_to_blue, interval=0.0005)
        Write.Print("@d1n0tf", Colors.blue_to_cyan, interval=0.0005)
        Write.Print("\n    • LOLZ: ", Colors.cyan_to_blue, interval=0.0005)
        Write.Print("d1n0", Colors.blue_to_cyan, interval=0.0005)
        Write.Print("\n    • GitHub: ", Colors.cyan_to_blue, interval=0.0005)
        Write.Print("d1n0tf", Colors.blue_to_cyan, interval=0.0005)
        Write.Print("\n", Colors.cyan_to_blue, interval=0.0005)
        Write.Print("\n    [+] Разработчик оригинала:\n", Colors.cyan_to_blue, interval=0.0005)
        Write.Print("\n    • Telegram: ", Colors.cyan_to_blue, interval=0.0005)
        Write.Print("@klintxxxgod", Colors.blue_to_cyan, interval=0.0005)
        Write.Print("\n    • LOLZ: ", Colors.cyan_to_blue, interval=0.0005)
        Write.Print("KLINTXXXGOD", Colors.blue_to_cyan, interval=0.0005)
        Write.Print("\n    • BHF: ", Colors.cyan_to_blue, interval=0.0005)
        Write.Print("KLINTXXXGOD", Colors.blue_to_cyan, interval=0.0005)
        Write.Print("\n    • GitHub: ", Colors.cyan_to_blue, interval=0.0005)
        Write.Print("klintxxxgod", Colors.blue_to_cyan, interval=0.0005)
        Write.Print("\n\n    Нажмите Enter для продолжения...", Colors.blue_to_cyan, interval=0.0005)
        input()
    elif choice == "12":
        Write.Print("\n    [+] Открываю документацию в браузере...\n", Colors.cyan_to_blue, interval=0.0005)
        webbrowser.open("https://github.com/d1n0tf/TeleToolProxified")
        Write.Print("\n    Нажмите Enter для продолжения...", Colors.blue_to_cyan, interval=0.0005)
        input()
    elif choice == "13":
        proxy_manager_menu()
    elif choice == "14":
        Write.Print("\n    [+] Завершение работы...\n", Colors.cyan_to_blue, interval=0.0005)
        break
    else:
        Write.Print("\n    [!] Неверный выбор. Повторите попытку.\n", Colors.red, interval=0.0005)
        Write.Print("\n    Нажмите Enter для продолжения...", Colors.blue_to_cyan, interval=0.0005)
        input()
