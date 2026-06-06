import configparser
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Optional

from telethon import TelegramClient


CONFIG_PATH = Path("config.ini")
DEVICE_CATALOG_PATH = Path("src/set_apps.json")


class ConfigurationError(Exception):
    pass


@dataclass(frozen=True)
class DeviceProfile:
    device_id: int
    device_model: str
    system_version: str
    app_version: str


@dataclass(frozen=True)
class OperationSettings:
    section_name: str
    api_id: int
    api_hash: str
    device: Optional[DeviceProfile] = None


def read_config(config_path: Path = CONFIG_PATH) -> configparser.ConfigParser:
    config = configparser.ConfigParser()
    config.read(config_path, encoding="utf-8")
    return config


def write_config(config: configparser.ConfigParser, config_path: Path = CONFIG_PATH) -> None:
    with config_path.open("w", encoding="utf-8") as file:
        config.write(file)


def ensure_section(config: configparser.ConfigParser, section_name: str) -> None:
    if section_name not in config:
        config[section_name] = {}


def load_device_catalog() -> List[dict]:
    try:
        with DEVICE_CATALOG_PATH.open("r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError as exc:
        raise ConfigurationError("Не найден файл src/set_apps.json") from exc
    except json.JSONDecodeError as exc:
        raise ConfigurationError("Файл src/set_apps.json поврежден или имеет неверный формат") from exc


def load_device_profile(device_id: int) -> DeviceProfile:
    devices = load_device_catalog()

    try:
        device = devices[device_id]
    except IndexError as exc:
        raise ConfigurationError("Указан несуществующий device_id") from exc

    try:
        return DeviceProfile(
            device_id=device_id,
            device_model=str(device["device_model"]),
            system_version=str(device["system_version"]),
            app_version=str(device["app_version"]),
        )
    except KeyError as exc:
        raise ConfigurationError("В выбранном устройстве отсутствуют обязательные поля") from exc


def load_operation_settings(section_name: str, require_device: bool = True) -> OperationSettings:
    config = read_config()

    if section_name not in config:
        raise ConfigurationError(f"В config.ini отсутствует секция [{section_name}]")

    section = config[section_name]
    api_id_raw = str(section.get("api_id", "")).strip()
    api_hash = str(section.get("api_hash", "")).strip()

    if not api_id_raw or not api_hash:
        raise ConfigurationError(
            f"В секции [{section_name}] не настроены api_id/api_hash"
        )

    try:
        api_id = int(api_id_raw)
    except ValueError as exc:
        raise ConfigurationError(f"В секции [{section_name}] указан некорректный api_id") from exc

    device = None
    if require_device:
        device_id_raw = str(section.get("device_id", "")).strip()
        if not device_id_raw:
            raise ConfigurationError(f"В секции [{section_name}] не настроен device_id")

        try:
            device = load_device_profile(int(device_id_raw))
        except ValueError as exc:
            raise ConfigurationError(f"В секции [{section_name}] указан некорректный device_id") from exc

    return OperationSettings(
        section_name=section_name,
        api_id=api_id,
        api_hash=api_hash,
        device=device,
    )


def build_telegram_client(
    session_name,
    settings: OperationSettings,
    proxy=None,
    **extra_kwargs,
) -> TelegramClient:
    client_kwargs = {
        "proxy": proxy,
    }

    if settings.device is not None:
        client_kwargs.update(
            {
                "device_model": settings.device.device_model,
                "system_version": settings.device.system_version,
                "app_version": settings.device.app_version,
            }
        )

    client_kwargs.update(extra_kwargs)

    return TelegramClient(
        str(session_name),
        settings.api_id,
        settings.api_hash,
        **client_kwargs,
    )


def collect_session_files(directory: str) -> List[Path]:
    session_dir = Path(directory)
    session_dir.mkdir(parents=True, exist_ok=True)
    return sorted(session_dir.glob("*.session"), key=lambda path: path.name.lower())


def format_session_name(session_path: Path) -> str:
    return session_path.name


def build_proxy_status_line(mode_name: str, proxy_count: int, account_count: int) -> str:
    return (
        f"Режим прокси: {mode_name} | Прокси: {proxy_count} | Аккаунтов: {account_count}"
    )


def iter_device_labels() -> Iterable[str]:
    for index, device in enumerate(load_device_catalog(), start=1):
        yield f"{index:02d} | {device['device_model']} ({device['system_version']})"
