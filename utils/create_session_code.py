import asyncio
import os

import telethon
from pystyle import Colors, Write

from .proxy_manager import ProxyConfigurationError, ProxyManager
from .runtime_config import ConfigurationError, build_telegram_client, load_operation_settings


async def create_session_code():
    client = None

    try:
        settings = load_operation_settings("CODE", require_device=True)
    except ConfigurationError as exc:
        Write.Print(f"\n    [!] {exc}\n", Colors.red, interval=0.0005)
        return False

    try:
        proxy_manager = ProxyManager.from_config()
    except ProxyConfigurationError as exc:
        Write.Print(f"\n    [!] {exc}\n", Colors.red, interval=0.0005)
        return False

    if proxy_manager.settings.enabled and proxy_manager.invalid_lines:
        Write.Print(
            f"\n    [!] Пропущено некорректных строк прокси: {len(proxy_manager.invalid_lines)}\n",
            Colors.yellow,
            interval=0.0005,
        )

    proxy_plan = proxy_manager.build_plan(["manual_code_login"], key_getter=lambda item: str(item))
    proxy_assignment = proxy_plan[0]

    try:
        os.makedirs("results/create_session_code/sessios", exist_ok=True)

        if os.path.exists("results/create_session_code/sessios/temp_session.session"):
            try:
                os.remove("results/create_session_code/sessios/temp_session.session")
            except PermissionError:
                Write.Print(
                    "\n    [!] Не удалось удалить старый файл сессии. Возможно, он используется другим процессом.\n",
                    Colors.yellow,
                    interval=0.0005,
                )
                return False

        if proxy_manager.settings.enabled:
            Write.Print(
                f"\n    [*] Используем прокси: {proxy_assignment.proxy_label}\n",
                Colors.blue_to_cyan,
                interval=0.0005,
            )

        client = build_telegram_client(
            "results/create_session_code/sessios/temp_session",
            settings,
            proxy=proxy_assignment.proxy.to_telethon_proxy() if proxy_assignment.proxy else None,
        )
        await client.connect()

        try:
            Write.Print(
                "\n    Введите номер телефона (в международном формате): ",
                Colors.cyan,
                interval=0.0005,
            )
            phone = input()

            try:
                await client.send_code_request(phone)
            except telethon.errors.PhoneCodeInvalidError as exc:
                Write.Print(
                    "\n    [!] Ошибка: код подтверждения недействителен. Проверьте номер телефона и попробуйте снова.\n",
                    Colors.red,
                    interval=0.0005,
                )
                Write.Print(
                    f"    [!] Подробности ошибки: {exc}\n",
                    Colors.red,
                    interval=0.0005,
                )
                return False

            Write.Print("\n    Введите код подтверждения: ", Colors.cyan, interval=0.0005)
            code = input()

            try:
                await client.sign_in(phone, code)
            except telethon.errors.SessionPasswordNeededError:
                Write.Print(
                    "\n    [!] Требуется двухфакторная аутентификация\n",
                    Colors.yellow,
                    interval=0.0005,
                )
                password = input("    Введите пароль 2FA: ")
                await client.sign_in(password=password)

            if not await client.is_user_authorized():
                Write.Print("\n    [!] Не удалось авторизоваться\n", Colors.red, interval=0.0005)
                return False

            Write.Print("\n    [+] Успешная авторизация!\n", Colors.cyan_to_blue, interval=0.0005)

            me = await client.get_me()
            phone = me.phone

            await client.disconnect()
            await asyncio.sleep(1)

            max_attempts = 3
            for attempt in range(max_attempts):
                try:
                    os.rename(
                        "results/create_session_code/sessios/temp_session.session",
                        f"results/create_session_code/sessios/{phone}.session",
                    )
                    Write.Print(
                        f"\n    [+] Файл сессии сохранен как: results/create_session_code/sessios/{phone}.session\n",
                        Colors.cyan_to_blue,
                        interval=0.0005,
                    )
                    break
                except PermissionError:
                    if attempt == max_attempts - 1:
                        Write.Print(
                            "\n    [!] Не удалось переименовать файл сессии после нескольких попыток.\n",
                            Colors.yellow,
                            interval=0.0005,
                        )
                        return False
                    await asyncio.sleep(1)

            return True
        except Exception as exc:
            Write.Print(f"\n    [!] Ошибка: {exc}\n", Colors.red, interval=0.0005)
            return False
    except Exception as exc:
        Write.Print(f"\n    [!] Ошибка: {exc}\n", Colors.red, interval=0.0005)
        return False
    finally:
        if client and client.is_connected():
            await client.disconnect()
