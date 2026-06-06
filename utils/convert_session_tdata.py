import logging
import os

from opentele.api import UseCurrentSession
from pystyle import Colors, Write

from .proxy_manager import ProxyConfigurationError, ProxyManager
from .runtime_config import (
    ConfigurationError,
    build_telegram_client,
    collect_session_files,
    load_operation_settings,
)


logging.basicConfig(
    filename="results/session_to_tdata/converter.log",
    filemode="a",
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)


async def session_to_tdata_convert():
    sessions_dir = "results/session_to_tdata/sessions"
    tdatas_dir = "results/session_to_tdata/tdatas"

    os.makedirs(sessions_dir, exist_ok=True)
    os.makedirs(tdatas_dir, exist_ok=True)

    session_files = collect_session_files(sessions_dir)
    if not session_files:
        logging.error("В директории %s не найдено .session файлов", sessions_dir)
        Write.Print("\n    [!] Не найдено .session файлов в директории\n", Colors.red, interval=0.0005)
        return False

    try:
        settings = load_operation_settings("STD", require_device=True)
    except ConfigurationError as exc:
        Write.Print(f"\n    [!] {exc}\n", Colors.red, interval=0.0005)
        return False

    try:
        proxy_manager = ProxyManager.from_config()
    except ProxyConfigurationError as exc:
        Write.Print(f"\n    [!] {exc}\n", Colors.red, interval=0.0005)
        return False

    proxy_plan = proxy_manager.build_plan(session_files, key_getter=lambda path: path.stem)
    total_files = len(proxy_plan)
    success_count = 0

    Write.Print(
        f"\n    [*] {proxy_manager.describe(total_files)}\n",
        Colors.blue_to_cyan,
        interval=0.0005,
    )
    if proxy_manager.settings.enabled:
        plan_path = proxy_manager.write_plan("session_to_tdata", proxy_plan)
        Write.Print(
            f"    [*] План прокси сохранен: {plan_path}\n",
            Colors.blue_to_cyan,
            interval=0.0005,
        )
        if proxy_manager.invalid_lines:
            Write.Print(
                f"    [!] Пропущено некорректных строк прокси: {len(proxy_manager.invalid_lines)}\n",
                Colors.yellow,
                interval=0.0005,
            )

    for assignment in proxy_plan:
        session_file = assignment.item
        client = None

        try:
            logging.info("Конвертация файла: %s", session_file)
            Write.Print(
                f"\n    [*] Конвертация файла: {session_file.name} | Proxy: {assignment.proxy_label}\n",
                Colors.blue_to_cyan,
                interval=0.0005,
            )

            client = build_telegram_client(
                session_file,
                settings,
                proxy=assignment.proxy.to_telethon_proxy() if assignment.proxy else None,
                receive_updates=False,
            )
            await client.connect()

            if not await client.is_user_authorized():
                Write.Print(
                    f"    [!] Сессия {session_file.name} не авторизована\n",
                    Colors.red,
                    interval=0.0005,
                )
                continue

            tdesk = await client.ToTDesktop(flag=UseCurrentSession)
            tdata_path = os.path.join(tdatas_dir, session_file.stem)

            if os.path.exists(tdata_path):
                for root, dirs, files in os.walk(tdata_path, topdown=False):
                    for name in files:
                        os.remove(os.path.join(root, name))
                    for name in dirs:
                        os.rmdir(os.path.join(root, name))
                os.rmdir(tdata_path)

            os.makedirs(tdata_path)
            tdesk.SaveTData(tdata_path)

            success_count += 1
            logging.info("Успешно конвертирован файл: %s", session_file.name)
            Write.Print(
                f"    [+] Успешно конвертирован файл: {session_file.name}\n",
                Colors.cyan_to_blue,
                interval=0.0005,
            )
        except Exception as exc:
            logging.error("Ошибка при конвертации %s: %s", session_file, exc)
            Write.Print(
                f"    [!] Ошибка при конвертации {session_file.name}: {exc}\n",
                Colors.red,
                interval=0.0005,
            )
        finally:
            if client and client.is_connected():
                await client.disconnect()

    if success_count > 0:
        logging.info("Конвертировано успешно: %s из %s файлов", success_count, total_files)
        Write.Print(
            f"\n    [+] Конвертировано успешно: {success_count} из {total_files} файлов\n",
            Colors.cyan_to_blue,
            interval=0.0005,
        )
        return True

    logging.error("Не удалось конвертировать ни одного файла")
    Write.Print("\n    [!] Не удалось конвертировать ни одного файла\n", Colors.red, interval=0.0005)
    return False
