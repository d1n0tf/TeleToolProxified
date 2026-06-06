import os
from pathlib import Path

from pystyle import Colors, Colorate, Write

from utils.proxy_manager import (
    DEFAULT_PROXY_MODE,
    PROXY_MODE_DESCRIPTIONS,
    PROXY_MODE_LABELS,
    ProxyConfigurationError,
    ensure_proxy_defaults,
    load_proxies,
    load_proxy_settings_safe,
    validate_proxy_runtime_support,
)
from utils.runtime_config import read_config, write_config

from .banner import banner, print_header, print_menu_item, print_separator


MODE_ORDER = [
    "chunked_round_robin",
    "round_robin",
    "sticky_hash",
    "single",
]


def _print_invalid_proxy_preview(invalid_lines, limit: int = 3) -> None:
    for issue in invalid_lines[:limit]:
        Write.Print(f"    [!] {issue}\n", Colors.yellow, interval=0.0005)

    remaining = len(invalid_lines) - limit
    if remaining > 0:
        Write.Print(
            f"    [!] И еще строк с ошибками: {remaining}\n",
            Colors.yellow,
            interval=0.0005,
        )


def _open_path(path: str) -> None:
    absolute_path = Path(os.path.abspath(path))

    if absolute_path.suffix:
        absolute_path.parent.mkdir(parents=True, exist_ok=True)
    else:
        absolute_path.mkdir(parents=True, exist_ok=True)

    if not absolute_path.exists() and absolute_path.suffix == ".txt":
        with absolute_path.open("a", encoding="utf-8"):
            pass

    if os.name == "nt":
        os.startfile(str(absolute_path))
    else:
        os.system(f'xdg-open "{absolute_path}"')


def _toggle_proxy_enabled():
    config = read_config()
    ensure_proxy_defaults(config)

    enabled = config["PROXY"].getboolean("enabled", fallback=False)
    if enabled:
        config["PROXY"]["enabled"] = "false"
        write_config(config)
        Write.Print("\n    [+] Прокси выключены\n", Colors.cyan_to_blue, interval=0.0005)
        return

    settings, warning = load_proxy_settings_safe()
    if warning or settings.mode == "disabled":
        config["PROXY"]["mode"] = DEFAULT_PROXY_MODE
        write_config(config)
        settings, _ = load_proxy_settings_safe()

        if warning:
            Write.Print(
                f"\n    [!] Некорректный режим в config.ini. Установлен режим по умолчанию: {DEFAULT_PROXY_MODE}\n",
                Colors.yellow,
                interval=0.0005,
            )
        else:
            Write.Print(
                f"\n    [!] В config.ini был указан режим без прокси. Для включения выбран режим по умолчанию: {DEFAULT_PROXY_MODE}\n",
                Colors.yellow,
                interval=0.0005,
            )

    try:
        validate_proxy_runtime_support()
        proxies, invalid_lines = load_proxies(settings.proxy_file)
    except ProxyConfigurationError as exc:
        Write.Print(f"\n    [!] {exc}\n", Colors.red, interval=0.0005)
        return

    if not proxies:
        Write.Print(
            f"\n    [!] В файле {settings.proxy_file} нет валидных прокси для включения\n",
            Colors.red,
            interval=0.0005,
        )
        if invalid_lines:
            _print_invalid_proxy_preview(invalid_lines)
        return

    config["PROXY"]["enabled"] = "true"
    write_config(config)

    Write.Print(
        f"\n    [+] Прокси включены. Валидных прокси: {len(proxies)}\n",
        Colors.cyan_to_blue,
        interval=0.0005,
    )
    if invalid_lines:
        Write.Print(
            f"    [!] Некорректных строк пропущено: {len(invalid_lines)}\n",
            Colors.yellow,
            interval=0.0005,
        )
        _print_invalid_proxy_preview(invalid_lines)


def _select_proxy_mode():
    settings, warning = load_proxy_settings_safe()
    if warning:
        Write.Print(f"\n    [!] {warning}\n", Colors.yellow, interval=0.0005)

    Write.Print("\n    Доступные режимы прокси:\n", Colors.cyan, interval=0.0005)
    for index, mode_name in enumerate(MODE_ORDER, start=1):
        recommended = " (Recommended)" if mode_name == "chunked_round_robin" else ""
        Write.Print(
            f"    {index}. {PROXY_MODE_LABELS[mode_name]}{recommended}\n",
            Colors.blue_to_cyan,
            interval=0.0005,
        )
        Write.Print(
            f"       {PROXY_MODE_DESCRIPTIONS[mode_name]}\n",
            Colors.blue_to_cyan,
            interval=0.0005,
        )

    Write.Print(
        f"\n    Текущий режим: {settings.mode_label}\n",
        Colors.cyan_to_blue,
        interval=0.0005,
    )
    Write.Print("    Выберите режим > ", Colors.blue_to_cyan, interval=0.0005)
    choice = input().strip()

    try:
        mode_index = int(choice) - 1
    except ValueError:
        Write.Print("\n    [!] Введите корректный номер режима\n", Colors.red, interval=0.0005)
        return

    if mode_index < 0 or mode_index >= len(MODE_ORDER):
        Write.Print("\n    [!] Выбран несуществующий режим\n", Colors.red, interval=0.0005)
        return

    config = read_config()
    ensure_proxy_defaults(config)
    config["PROXY"]["mode"] = MODE_ORDER[mode_index]
    write_config(config)

    Write.Print(
        f"\n    [+] Режим прокси изменен: {PROXY_MODE_LABELS[MODE_ORDER[mode_index]]}\n",
        Colors.cyan_to_blue,
        interval=0.0005,
    )


def _show_proxy_status():
    settings, warning = load_proxy_settings_safe()

    Write.Print("\n    Текущие настройки прокси:\n", Colors.cyan, interval=0.0005)
    if warning:
        Write.Print(f"    [!] {warning}\n", Colors.yellow, interval=0.0005)
    Write.Print(
        f"    [+] Статус: {'включены' if settings.enabled else 'выключены'}\n",
        Colors.blue_to_cyan,
        interval=0.0005,
    )
    Write.Print(
        f"    [+] Режим: {settings.mode_label}\n",
        Colors.blue_to_cyan,
        interval=0.0005,
    )
    Write.Print(
        f"    [+] Файл: {settings.proxy_file}\n",
        Colors.blue_to_cyan,
        interval=0.0005,
    )
    try:
        validate_proxy_runtime_support()
        Write.Print("    [+] Proxy-зависимости установлены\n", Colors.cyan_to_blue, interval=0.0005)
    except ProxyConfigurationError as exc:
        Write.Print(f"    [!] {exc}\n", Colors.yellow, interval=0.0005)

    try:
        proxies, invalid_lines = load_proxies(settings.proxy_file)
    except ProxyConfigurationError as exc:
        Write.Print(f"    [!] {exc}\n", Colors.red, interval=0.0005)
        return

    Write.Print(
        f"    [+] Загружено прокси: {len(proxies)}\n",
        Colors.blue_to_cyan,
        interval=0.0005,
    )
    if invalid_lines:
        Write.Print(
            f"    [!] Некорректных строк: {len(invalid_lines)}\n",
            Colors.yellow,
            interval=0.0005,
        )
        _print_invalid_proxy_preview(invalid_lines)
    else:
        Write.Print(
            "    [+] Все строки в файле прокси выглядят валидно\n",
            Colors.cyan_to_blue,
            interval=0.0005,
        )


def proxy_manager_menu():
    while True:
        settings, warning = load_proxy_settings_safe()
        toggle_label = "Выключить прокси" if settings.enabled else "Включить прокси"
        toggle_description = (
            "Сейчас: включены" if settings.enabled else "Сейчас: выключены"
        )

        os.system("clear" if os.name == "posix" else "cls")
        print(Colorate.Diagonal(Colors.blue_to_cyan, banner))
        print_separator()

        print_header("PROXY MANAGER")
        print_menu_item("1", toggle_label, toggle_description)
        print_menu_item("2", "Сменить режим", "Ротация и распределение аккаунтов")
        print_menu_item("3", "Открыть proxies.txt", "Редактирование списка прокси")
        print_menu_item("4", "Открыть планы", "Последние JSON-планы распределения")
        print_menu_item("5", "Показать статус", "Текущие настройки и число валидных прокси")
        print_menu_item("6", "Назад", "Вернуться в главное меню")
        if warning:
            Write.Print(f"\n    [!] {warning}\n", Colors.yellow, interval=0.0005)

        print_separator()
        Write.Print("\n    > Выберите пункт меню: ", Colors.cyan_to_blue, interval=0.0005)
        choice = input().strip()

        if choice == "1":
            _toggle_proxy_enabled()
            Write.Print("\n    Нажмите Enter для продолжения...", Colors.blue_to_cyan, interval=0.0005)
            input()
        elif choice == "2":
            _select_proxy_mode()
            Write.Print("\n    Нажмите Enter для продолжения...", Colors.blue_to_cyan, interval=0.0005)
            input()
        elif choice == "3":
            _open_path("proxies.txt")
        elif choice == "4":
            _open_path("results/proxy_plans")
        elif choice == "5":
            _show_proxy_status()
            Write.Print("\n    Нажмите Enter для продолжения...", Colors.blue_to_cyan, interval=0.0005)
            input()
        elif choice == "6":
            return
        else:
            Write.Print("\n    [!] Неверный выбор\n", Colors.red, interval=0.0005)
            Write.Print("\n    Нажмите Enter для продолжения...", Colors.blue_to_cyan, interval=0.0005)
            input()
