import logging

from pystyle import Colors, Write
from telethon.tl.types import Channel, Chat, User

from .proxy_manager import ProxyConfigurationError, ProxyManager
from .runtime_config import (
    ConfigurationError,
    build_telegram_client,
    collect_session_files,
    load_operation_settings,
)


logging.basicConfig(
    filename="results/cleaner/cleaner.log",
    filemode="a",
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)


def _matches_dialog_type(entity, dialog_type):
    if dialog_type == "user":
        return isinstance(entity, User) and not entity.bot
    if dialog_type == "chat":
        return isinstance(entity, Chat)
    if dialog_type == "channel":
        return isinstance(entity, Channel) and not entity.megagroup
    if dialog_type == "bot":
        return isinstance(entity, User) and entity.bot
    return False


def _dialog_title(entity):
    if hasattr(entity, "title") and entity.title:
        return entity.title
    if hasattr(entity, "first_name") and entity.first_name:
        return entity.first_name
    if hasattr(entity, "username") and entity.username:
        return entity.username
    return "unknown"


def _prepare_cleaner_plan(operation_name):
    session_files = collect_session_files("results/cleaner/sessions")
    if not session_files:
        Write.Print(
            "\n    [!] Не найдены .session файлы в папке results/cleaner/sessions\n",
            Colors.red,
            interval=0.0005,
        )
        return None, None, None

    try:
        settings = load_operation_settings("DLG", require_device=True)
    except ConfigurationError as exc:
        Write.Print(f"\n    [!] {exc}\n", Colors.red, interval=0.0005)
        return None, None, None

    try:
        proxy_manager = ProxyManager.from_config()
    except ProxyConfigurationError as exc:
        Write.Print(f"\n    [!] {exc}\n", Colors.red, interval=0.0005)
        return None, None, None

    proxy_plan = proxy_manager.build_plan(session_files, key_getter=lambda path: path.stem)
    Write.Print(
        f"\n    [*] {proxy_manager.describe(len(proxy_plan))}\n",
        Colors.blue_to_cyan,
        interval=0.0005,
    )

    if proxy_manager.settings.enabled:
        plan_path = proxy_manager.write_plan(operation_name, proxy_plan)
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

    return settings, proxy_manager, proxy_plan


async def count_dialogs(dialog_type):
    settings, _, proxy_plan = _prepare_cleaner_plan(f"cleaner_count_{dialog_type}")
    if not settings or proxy_plan is None:
        return False

    total_count = 0
    processed_accounts = 0

    for assignment in proxy_plan:
        session_file = assignment.item
        client = None

        try:
            Write.Print(
                f"\n    [*] Подсчет в {session_file.name} | Proxy: {assignment.proxy_label}\n",
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

            account_count = 0
            async for dialog in client.iter_dialogs():
                if _matches_dialog_type(dialog.entity, dialog_type):
                    account_count += 1

            total_count += account_count
            processed_accounts += 1
            logging.info("Подсчитано %s %s(ов) в %s", account_count, dialog_type, session_file.name)
            Write.Print(
                f"    [+] Найдено {account_count} {dialog_type}(ов) в {session_file.name}\n",
                Colors.cyan_to_blue,
                interval=0.0005,
            )
        except Exception as exc:
            logging.error("Ошибка при подсчете диалогов в %s: %s", session_file, exc)
            Write.Print(f"    [!] Ошибка: {exc}\n", Colors.red, interval=0.0005)
        finally:
            if client and client.is_connected():
                await client.disconnect()

    if processed_accounts == 0:
        return False

    Write.Print(
        f"\n    [+] Итого найдено {total_count} {dialog_type}(ов) в {processed_accounts} аккаунтах\n",
        Colors.cyan_to_blue,
        interval=0.0005,
    )
    return total_count


async def clean_dialogs(dialog_type):
    settings, _, proxy_plan = _prepare_cleaner_plan(f"cleaner_clean_{dialog_type}")
    if not settings or proxy_plan is None:
        return False

    affected_dialogs = 0
    processed_accounts = 0

    for assignment in proxy_plan:
        session_file = assignment.item
        client = None

        try:
            Write.Print(
                f"\n    [*] Очистка {session_file.name} | Proxy: {assignment.proxy_label}\n",
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

            account_deleted = 0
            async for dialog in client.iter_dialogs():
                entity = dialog.entity
                if not _matches_dialog_type(entity, dialog_type):
                    continue

                try:
                    await client.delete_dialog(entity)
                    account_deleted += 1
                    affected_dialogs += 1
                    Write.Print(
                        f"    [+] Удален диалог: {_dialog_title(entity)}\n",
                        Colors.cyan_to_blue,
                        interval=0.0005,
                    )
                except Exception as exc:
                    Write.Print(
                        f"    [!] Ошибка при удалении диалога {_dialog_title(entity)}: {exc}\n",
                        Colors.red,
                        interval=0.0005,
                    )

            processed_accounts += 1
            logging.info("Удалено %s %s(ов) в %s", account_deleted, dialog_type, session_file.name)
            Write.Print(
                f"    [+] В {session_file.name} очищено {account_deleted} {dialog_type}(ов)\n",
                Colors.cyan_to_blue,
                interval=0.0005,
            )
        except Exception as exc:
            logging.error("Ошибка при очистке диалогов в %s: %s", session_file, exc)
            Write.Print(f"    [!] Ошибка: {exc}\n", Colors.red, interval=0.0005)
        finally:
            if client and client.is_connected():
                await client.disconnect()

    if processed_accounts == 0:
        return False

    Write.Print(
        f"\n    [+] Успешно удалено/очищено {affected_dialogs} {dialog_type}(ов) в {processed_accounts} аккаунтах\n",
        Colors.cyan_to_blue,
        interval=0.0005,
    )
    return True
