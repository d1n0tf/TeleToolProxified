import asyncio
import configparser
import json
import os

from colorama import *
from pystyle import Colors, Colorate, Write

from menu import banner, print_separator


def session_to_tdata_menu():
    while True:
        os.system("clear" if os.name == "posix" else "cls")
        print(Colorate.Diagonal(Colors.blue_to_cyan, banner))
        print_separator()
        Write.Print("\n    ┏━━ Выберите действие:\n", Colors.cyan, interval=0.0005)
        Write.Print("    ┃ 1 ┃ Настроить device\n", Colors.blue_to_cyan, interval=0.0005)
        Write.Print("    ┃ 2 ┃ Настроить API id and hash\n", Colors.blue_to_cyan, interval=0.0005)
        Write.Print("    ┃ 3 ┃ Открыть директорию для загрузки данных\n", Colors.blue_to_cyan, interval=0.0005)
        Write.Print("    ┃ 4 ┃ Открыть директорию для получения результатов\n", Colors.blue_to_cyan, interval=0.0005)
        Write.Print("    ┃ 5 ┃ Начать конвертацию\n", Colors.blue_to_cyan, interval=0.0005)
        Write.Print("    ┃ 6 ┃ Выйти в главное меню\n", Colors.blue_to_cyan, interval=0.0005)
        print_separator()
        Write.Print("\n    > Выберите пункт меню: ", Colors.cyan_to_blue, interval=0.0005)
        subchoice = input().strip()

        if subchoice == "1":
            try:
                with open("src/set_apps.json", "r", encoding="utf-8") as file:
                    devices = json.load(file)

                Write.Print("\n    Доступные устройства:\n", Colors.cyan, interval=0.0005)
                for index, device in enumerate(devices, start=1):
                    Write.Print(
                        f"    {index:02d} | {device['device_model']} ({device['system_version']})\n",
                        Colors.blue_to_cyan,
                        interval=0.0005,
                    )

                Write.Print("\n    Введите номер устройства > ", Colors.blue_to_cyan, interval=0.0005)
                device_num = input().strip()

                try:
                    device_num_int = int(device_num)
                except ValueError:
                    Write.Print("\n    [!] Введите корректный номер\n", Colors.red, interval=0.0005)
                    Write.Print("\n    Нажмите Enter для продолжения...", Colors.blue_to_cyan, interval=0.0005)
                    input()
                    continue

                if not 1 <= device_num_int <= len(devices):
                    Write.Print("\n    [!] Неверный номер устройства\n", Colors.red, interval=0.0005)
                    Write.Print("\n    Нажмите Enter для продолжения...", Colors.blue_to_cyan, interval=0.0005)
                    input()
                    continue

                config = configparser.ConfigParser()
                config.read("config.ini", encoding="utf-8")
                if "STD" not in config:
                    config["STD"] = {}
                config["STD"]["device_id"] = str(device_num_int - 1)

                with open("config.ini", "w", encoding="utf-8") as file:
                    config.write(file)

                Write.Print(
                    f"\n    [+] Устройство {devices[device_num_int - 1]['device_model']} успешно установлено\n",
                    Colors.cyan_to_blue,
                    interval=0.0005,
                )
            except Exception as exc:
                Write.Print(f"\n    [!] Ошибка: {exc}\n", Colors.red, interval=0.0005)

            Write.Print("\n    Нажмите Enter для продолжения...", Colors.blue_to_cyan, interval=0.0005)
            input()
        elif subchoice == "2":
            try:
                Write.Print("\n    Введите API ID > ", Colors.blue_to_cyan, interval=0.0005)
                api_id = input().strip()

                Write.Print("    Введите API Hash > ", Colors.blue_to_cyan, interval=0.0005)
                api_hash = input().strip()

                config = configparser.ConfigParser()
                config.read("config.ini", encoding="utf-8")
                if "STD" not in config:
                    config["STD"] = {}
                config["STD"]["api_id"] = api_id
                config["STD"]["api_hash"] = api_hash

                with open("config.ini", "w", encoding="utf-8") as file:
                    config.write(file)

                Write.Print("\n    [+] API данные успешно сохранены\n", Colors.cyan_to_blue, interval=0.0005)
            except Exception as exc:
                Write.Print(f"\n    [!] Ошибка: {exc}\n", Colors.red, interval=0.0005)

            Write.Print("\n    Нажмите Enter для продолжения...", Colors.blue_to_cyan, interval=0.0005)
            input()
        elif subchoice == "3":
            try:
                folder_path = os.path.abspath("results/session_to_tdata/sessions")
                os.makedirs(folder_path, exist_ok=True)
                os.startfile(folder_path)
            except Exception:
                Write.Print("\n    Ошибка при открытии директории!\n", Colors.blue_to_cyan, interval=0.0005)
        elif subchoice == "4":
            try:
                folder_path = os.path.abspath("results/session_to_tdata/tdatas")
                os.makedirs(folder_path, exist_ok=True)
                os.startfile(folder_path)
            except Exception:
                Write.Print("\n    Ошибка при открытии директории!\n", Colors.blue_to_cyan, interval=0.0005)
        elif subchoice == "5":
            Write.Print("\n    [ ] Начинаем конвертацию файлов...\n", Colors.blue_to_cyan, interval=0.0005)
            try:
                from utils import session_to_tdata_convert

                result = asyncio.run(session_to_tdata_convert())
                if result:
                    Write.Print(
                        "\n    [+] Конвертация успешно завершена\n    [+] Результаты сохранены в папке results/session_to_tdata/tdatas\n",
                        Colors.cyan_to_blue,
                        interval=0.0005,
                    )
                else:
                    Write.Print(
                        "\n    [!] Ошибка анализа! Проверьте наличие .session файлов в папке sessions\n",
                        Colors.red,
                        interval=0.0005,
                    )
            except BaseException as exc:
                Write.Print(
                    f"\n    [!] Не удалось запустить конвертер: {exc}\n",
                    Colors.red,
                    interval=0.0005,
                )

            Write.Print("\n    Нажмите Enter для продолжения...", Colors.blue_to_cyan, interval=0.0005)
            input()
        elif subchoice == "6":
            return
        else:
            Write.Print("\n    [!] Неверный выбор\n", Colors.red, interval=0.0005)
            Write.Print("\n    Нажмите Enter для продолжения...", Colors.blue_to_cyan, interval=0.0005)
            input()
