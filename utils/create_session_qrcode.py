import asyncio
import os

import qrcode
import telethon
from pystyle import Colors, Write

from .proxy_manager import ProxyConfigurationError, ProxyManager
from .runtime_config import ConfigurationError, build_telegram_client, load_operation_settings


def gen_qr(token: str) -> str:
    return token


async def _finalize_session_file(phone: str) -> bool:
    await asyncio.sleep(1)

    max_attempts = 3
    for attempt in range(max_attempts):
        try:
            os.rename(
                "results/create_session_qrcode/sessios/temp_session.session",
                f"results/create_session_qrcode/sessios/{phone}.session",
            )
            Write.Print(
                f"\n    [+] Файл сессии сохранен как: results/create_session_qrcode/sessios/{phone}.session\n",
                Colors.cyan_to_blue,
                interval=0.0005,
            )
            return True
        except PermissionError:
            if attempt == max_attempts - 1:
                Write.Print(
                    "\n    [!] Не удалось переименовать файл сессии после нескольких попыток.\n",
                    Colors.yellow,
                    interval=0.0005,
                )
                return False
            await asyncio.sleep(1)

    return False


async def create_session_qr():
    client = None

    try:
        settings = load_operation_settings("QR", require_device=True)
    except ConfigurationError as exc:
        Write.Print(f"\n    [!] {exc}\n", Colors.red, interval=0.0005)
        return False

    if len(settings.api_hash) != 32:
        Write.Print(
            "\n    [!] Неверная длина API hash (должно быть 32 символа)\n",
            Colors.red,
            interval=0.0005,
        )
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

    proxy_plan = proxy_manager.build_plan(["manual_qr_login"], key_getter=lambda item: str(item))
    proxy_assignment = proxy_plan[0]

    try:
        os.makedirs("results/create_session_qrcode/sessios", exist_ok=True)

        if os.path.exists("results/create_session_qrcode/sessios/temp_session.session"):
            try:
                os.remove("results/create_session_qrcode/sessios/temp_session.session")
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
            "results/create_session_qrcode/sessios/temp_session",
            settings,
            proxy=proxy_assignment.proxy.to_telethon_proxy() if proxy_assignment.proxy else None,
        )
        await client.connect()

        try:
            qr_login = await client.qr_login()
            qr_token = gen_qr(qr_login.url)

            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(qr_token)
            qr.make(fit=True)

            Write.Print(
                "\n    Отсканируйте этот QR код в приложении Telegram:\n",
                Colors.cyan,
                interval=0.0005,
            )
            qr.print_ascii()

            Write.Print(
                "\n    Ожидание сканирования QR кода...\n",
                Colors.blue_to_cyan,
                interval=0.0005,
            )
            Write.Print("    Нажмите Enter для отмены\n", Colors.blue_to_cyan, interval=0.0005)

            login_task = asyncio.create_task(qr_login.wait(timeout=120))

            async def wait_enter():
                await asyncio.get_event_loop().run_in_executor(None, input)
                return True

            enter_task = asyncio.create_task(wait_enter())

            done, pending = await asyncio.wait(
                [login_task, enter_task],
                return_when=asyncio.FIRST_COMPLETED,
            )

            for task in pending:
                task.cancel()

            if enter_task in done:
                Write.Print("\n    [!] Отменено пользователем\n", Colors.yellow, interval=0.0005)
                return False

            if not await client.is_user_authorized():
                Write.Print(
                    "\n    [!] Требуется двухфакторная аутентификация\n",
                    Colors.yellow,
                    interval=0.0005,
                )
                try:
                    password = input("    Введите пароль 2FA: ")
                    await client.sign_in(password=password)
                    Write.Print(
                        "\n    [+] Успешная авторизация с 2FA!\n",
                        Colors.cyan_to_blue,
                        interval=0.0005,
                    )
                except Exception as exc:
                    Write.Print(
                        f"\n    [!] Ошибка при вводе пароля 2FA: {exc}\n",
                        Colors.red,
                        interval=0.0005,
                    )
                    return False

            if not await client.is_user_authorized():
                Write.Print("\n    [!] Не удалось авторизоваться\n", Colors.red, interval=0.0005)
                return False

            Write.Print("\n    [+] Успешная авторизация!\n", Colors.cyan_to_blue, interval=0.0005)

            me = await client.get_me()
            phone = me.phone

            await client.disconnect()
            return await _finalize_session_file(phone)
        except telethon.errors.rpcerrorlist.SessionPasswordNeededError:
            Write.Print("\n    [!] Требуется пароль 2FA\n", Colors.yellow, interval=0.0005)
            try:
                password = input("    Введите пароль 2FA: ")
                await client.sign_in(password=password)
                Write.Print(
                    "\n    [+] Успешная авторизация с 2FA!\n",
                    Colors.cyan_to_blue,
                    interval=0.0005,
                )

                me = await client.get_me()
                phone = me.phone

                await client.disconnect()
                return await _finalize_session_file(phone)
            except Exception as exc:
                Write.Print(
                    f"\n    [!] Ошибка при вводе пароля 2FA: {exc}\n",
                    Colors.red,
                    interval=0.0005,
                )
                return False
        except Exception as exc:
            Write.Print(f"\n    [!] Ошибка: {exc}\n", Colors.red, interval=0.0005)
            return False
    except Exception as exc:
        Write.Print(f"\n    [!] Ошибка: {exc}\n", Colors.red, interval=0.0005)
        return False
    finally:
        if client and client.is_connected():
            await client.disconnect()
