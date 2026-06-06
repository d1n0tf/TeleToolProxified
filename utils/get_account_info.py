import json
import logging
import os

from pystyle import Colors, Write
from telethon.tl.functions.account import GetAuthorizationsRequest as GetSessionsRequest
from telethon.tl.functions.contacts import GetContactsRequest

from .proxy_manager import ProxyConfigurationError, ProxyManager
from .runtime_config import (
    ConfigurationError,
    build_telegram_client,
    collect_session_files,
    load_operation_settings,
)


logging.basicConfig(
    filename="results/account_info_save/session_parser.log",
    filemode="a",
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)


async def account_info_save_info():
    sessions_dir = "results/account_info_save/sessions"
    dumps_dir = "results/account_info_save/dumps"

    os.makedirs(sessions_dir, exist_ok=True)
    os.makedirs(dumps_dir, exist_ok=True)

    session_files = collect_session_files(sessions_dir)
    if not session_files:
        logging.error("В директории %s не найдено .session файлов", sessions_dir)
        Write.Print("\n    [!] Не найдено .session файлов в директории\n", Colors.red, interval=0.0005)
        return False

    try:
        settings = load_operation_settings("CHECK", require_device=True)
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
        plan_path = proxy_manager.write_plan("account_info_save", proxy_plan)
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
            logging.info("Обработка файла: %s", session_file)
            Write.Print(
                f"\n    [*] Обработка файла: {session_file.name} | Proxy: {assignment.proxy_label}\n",
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
                logging.error("Сессия %s не авторизована", session_file.name)
                Write.Print(
                    f"    [!] Сессия {session_file.name} не авторизована\n",
                    Colors.red,
                    interval=0.0005,
                )
                continue

            me = await client.get_me()
            account_info = {
                "user_info": {
                    "user_id": me.id,
                    "first_name": me.first_name,
                    "last_name": me.last_name,
                    "username": me.username,
                    "phone": me.phone,
                    "premium": me.premium,
                    "verified": me.verified,
                    "restricted": me.restricted,
                    "scam": me.scam,
                    "fake": me.fake,
                    "bot": me.bot,
                    "lang_code": me.lang_code,
                    "access_hash": me.access_hash,
                }
            }

            dialogs = await client.get_dialogs()
            account_info["dialogs"] = []
            for dialog in dialogs:
                dialog_info = {
                    "id": dialog.id,
                    "name": dialog.name,
                    "title": dialog.title,
                    "is_user": dialog.is_user,
                    "is_group": dialog.is_group,
                    "is_channel": dialog.is_channel,
                    "unread_count": dialog.unread_count,
                    "unread_mentions_count": dialog.unread_mentions_count,
                    "entity_type": str(type(dialog.entity).__name__),
                }

                if dialog.entity:
                    entity_info = {"id": dialog.entity.id}
                    if hasattr(dialog.entity, "access_hash"):
                        entity_info["access_hash"] = dialog.entity.access_hash
                    if hasattr(dialog.entity, "username"):
                        entity_info["username"] = dialog.entity.username
                    if hasattr(dialog.entity, "participants_count"):
                        entity_info["participants_count"] = dialog.entity.participants_count
                    dialog_info["entity"] = entity_info

                account_info["dialogs"].append(dialog_info)

            sessions = await client(GetSessionsRequest())
            account_info["sessions"] = []
            for auth in sessions.authorizations:
                account_info["sessions"].append(
                    {
                        "hash": auth.hash,
                        "device_model": auth.device_model,
                        "platform": auth.platform,
                        "system_version": auth.system_version,
                        "api_id": auth.api_id,
                        "app_name": auth.app_name,
                        "app_version": auth.app_version,
                        "date_created": auth.date_created.isoformat(),
                        "date_active": auth.date_active.isoformat(),
                        "ip": auth.ip,
                        "country": auth.country,
                        "region": auth.region,
                    }
                )

            contacts = await client(GetContactsRequest(hash=0))
            account_info["contacts"] = []
            for user in contacts.users:
                account_info["contacts"].append(
                    {
                        "id": user.id,
                        "access_hash": user.access_hash,
                        "first_name": user.first_name,
                        "last_name": user.last_name,
                        "username": user.username,
                        "phone": user.phone,
                        "bot": user.bot,
                        "mutual_contact": user.mutual_contact,
                        "verified": user.verified,
                        "restricted": user.restricted,
                        "scam": user.scam,
                        "fake": user.fake,
                        "lang_code": user.lang_code if hasattr(user, "lang_code") else None,
                    }
                )

            json_filename = os.path.join(dumps_dir, f"{session_file.stem}_full_info.json")
            with open(json_filename, "w", encoding="utf-8") as file:
                json.dump(account_info, file, indent=4, ensure_ascii=False)

            success_count += 1
            logging.info("Успешно обработан файл: %s", session_file.name)
            Write.Print(
                f"    [+] Успешно обработан файл: {session_file.name}\n",
                Colors.cyan_to_blue,
                interval=0.0005,
            )
        except Exception as exc:
            logging.error("Ошибка при обработке файла %s: %s", session_file, exc)
            Write.Print(
                f"    [!] Ошибка при обработке файла {session_file.name}: {exc}\n",
                Colors.red,
                interval=0.0005,
            )
        finally:
            if client and client.is_connected():
                await client.disconnect()

    if success_count > 0:
        logging.info("Обработано успешно: %s из %s файлов", success_count, total_files)
        Write.Print(
            f"\n    [+] Обработано успешно: {success_count} из {total_files} файлов\n",
            Colors.cyan_to_blue,
            interval=0.0005,
        )
        return True

    logging.error("Не удалось обработать ни одного файла")
    Write.Print("\n    [!] Не удалось обработать ни одного файла\n", Colors.red, interval=0.0005)
    return False
