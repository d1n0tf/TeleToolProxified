import hashlib
import importlib.util
import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple
from urllib.parse import unquote, urlparse

from .runtime_config import read_config


PROXY_SECTION = "PROXY"
DEFAULT_PROXY_FILE = Path("proxies.txt")
DEFAULT_PROXY_MODE = "chunked_round_robin"
PLAN_OUTPUT_DIR = Path("results/proxy_plans")

PROXY_MODE_LABELS = {
    "disabled": "Без прокси",
    "single": "Один прокси на все аккаунты",
    "round_robin": "По кругу на каждый аккаунт",
    "sticky_hash": "Стабильная привязка по имени сессии",
    "chunked_round_robin": "Пакеты на прокси + обработка по кругу",
}

PROXY_MODE_DESCRIPTIONS = {
    "single": "Все аккаунты используют первый прокси из списка.",
    "round_robin": "Каждый следующий аккаунт получает следующий прокси по кругу.",
    "sticky_hash": "Одна и та же сессия стабильно привязывается к одному прокси.",
    "chunked_round_robin": "Аккаунты делятся на равные пачки по прокси, но обрабатываются по кругу.",
}


class ProxyConfigurationError(Exception):
    pass


@dataclass(frozen=True)
class ProxySettings:
    enabled: bool
    mode: str
    proxy_file: Path

    @property
    def mode_label(self) -> str:
        if not self.enabled:
            return PROXY_MODE_LABELS["disabled"]
        return PROXY_MODE_LABELS.get(self.mode, self.mode)


@dataclass(frozen=True)
class ProxyDefinition:
    scheme: str
    host: str
    port: int
    username: Optional[str] = None
    password: Optional[str] = None
    rdns: bool = True
    source_line: Optional[str] = None

    def to_telethon_proxy(self) -> Tuple[Any, ...]:
        return (
            self.scheme,
            self.host,
            self.port,
            self.rdns,
            self.username,
            self.password,
        )

    def masked_label(self) -> str:
        credentials = f"{self.username}@" if self.username else ""
        return f"{self.scheme}://{credentials}{self.host}:{self.port}"


@dataclass(frozen=True)
class ProxyAssignment:
    item: Any
    item_key: str
    order_index: int
    proxy: Optional[ProxyDefinition]
    proxy_index: Optional[int]
    group_index: Optional[int]
    group_position: int

    @property
    def proxy_label(self) -> str:
        if self.proxy is None:
            return "direct"
        return self.proxy.masked_label()


def ensure_proxy_defaults(config) -> None:
    if PROXY_SECTION not in config:
        config[PROXY_SECTION] = {}

    proxy_section = config[PROXY_SECTION]
    proxy_section.setdefault("enabled", "false")
    proxy_section.setdefault("mode", DEFAULT_PROXY_MODE)
    proxy_section.setdefault("proxy_file", str(DEFAULT_PROXY_FILE))


def normalize_proxy_mode(mode_name: str) -> str:
    normalized = str(mode_name or "").strip().lower()

    aliases = {
        "none": "disabled",
        "off": "disabled",
        "disable": "disabled",
        "disabled": "disabled",
        "single": "single",
        "first": "single",
        "rr": "round_robin",
        "round_robin": "round_robin",
        "round-robin": "round_robin",
        "sticky": "sticky_hash",
        "sticky_hash": "sticky_hash",
        "hash": "sticky_hash",
        "balanced": "chunked_round_robin",
        "chunked": "chunked_round_robin",
        "chunked_round_robin": "chunked_round_robin",
        "smart": "chunked_round_robin",
        "main": "chunked_round_robin",
    }

    if normalized not in aliases:
        raise ProxyConfigurationError(
            f"Неизвестный режим прокси: {mode_name}"
        )

    return aliases[normalized]


def load_proxy_settings() -> ProxySettings:
    config = read_config()
    ensure_proxy_defaults(config)
    proxy_section = config[PROXY_SECTION]

    proxy_file_value = str(proxy_section.get("proxy_file", DEFAULT_PROXY_FILE)).strip()
    proxy_file = Path(proxy_file_value) if proxy_file_value else DEFAULT_PROXY_FILE

    enabled = proxy_section.getboolean("enabled", fallback=False)
    raw_mode = proxy_section.get("mode", DEFAULT_PROXY_MODE)

    try:
        mode = normalize_proxy_mode(raw_mode)
    except ProxyConfigurationError:
        if enabled:
            raise
        mode = DEFAULT_PROXY_MODE

    if mode == "disabled":
        enabled = False

    return ProxySettings(enabled=enabled, mode=mode, proxy_file=proxy_file)


def load_proxy_settings_safe() -> Tuple[ProxySettings, Optional[str]]:
    config = read_config()
    ensure_proxy_defaults(config)
    proxy_section = config[PROXY_SECTION]

    proxy_file_value = str(proxy_section.get("proxy_file", DEFAULT_PROXY_FILE)).strip()
    proxy_file = Path(proxy_file_value) if proxy_file_value else DEFAULT_PROXY_FILE
    enabled = proxy_section.getboolean("enabled", fallback=False)
    raw_mode = proxy_section.get("mode", DEFAULT_PROXY_MODE)

    try:
        mode = normalize_proxy_mode(raw_mode)
        warning = None
    except ProxyConfigurationError:
        mode = DEFAULT_PROXY_MODE
        warning = (
            f"В config.ini указан неизвестный режим прокси '{raw_mode}'. "
            f"В интерфейсе временно используется '{DEFAULT_PROXY_MODE}'."
        )

    if mode == "disabled":
        enabled = False

    return ProxySettings(enabled=enabled, mode=mode, proxy_file=proxy_file), warning


def validate_proxy_runtime_support() -> None:
    if importlib.util.find_spec("python_socks") or importlib.util.find_spec("socks"):
        return

    raise ProxyConfigurationError(
        "Для работы с прокси не найдена библиотека PySocks/python_socks. "
        "Переустановите зависимости через 'pip install -r requirements.txt'."
    )


def parse_proxy_line(line: str) -> Optional[ProxyDefinition]:
    raw_line = line.strip()
    if not raw_line or raw_line.startswith("#") or raw_line.startswith(";"):
        return None

    if "://" in raw_line:
        parsed = urlparse(raw_line)
        try:
            parsed_port = parsed.port
        except ValueError as exc:
            raise ProxyConfigurationError(f"Некорректный порт в proxy URL: {raw_line}") from exc

        if not parsed.scheme or not parsed.hostname or parsed_port is None:
            raise ProxyConfigurationError(f"Некорректный proxy URL: {raw_line}")

        scheme = parsed.scheme.lower()
        _validate_proxy_scheme(scheme)

        return ProxyDefinition(
            scheme=scheme,
            host=parsed.hostname,
            port=parsed_port,
            username=unquote(parsed.username) if parsed.username else None,
            password=unquote(parsed.password) if parsed.password else None,
            source_line=raw_line,
        )

    parts = raw_line.split(":")
    if len(parts) == 2:
        host, port = parts
        scheme = "socks5"
        username = None
        password = None
    elif len(parts) == 4:
        host, port, username, password = parts
        scheme = "socks5"
    elif len(parts) == 3 and parts[0].lower() in ("socks5", "socks4", "http"):
        scheme, host, port = parts
        username = None
        password = None
    elif len(parts) == 5 and parts[0].lower() in ("socks5", "socks4", "http"):
        scheme, host, port, username, password = parts
    else:
        raise ProxyConfigurationError(
            f"Неподдерживаемый формат прокси: {raw_line}"
        )

    scheme = scheme.lower()
    _validate_proxy_scheme(scheme)

    try:
        port_number = int(str(port).strip())
    except ValueError as exc:
        raise ProxyConfigurationError(f"Некорректный порт в прокси: {raw_line}") from exc

    host_value = str(host).strip()
    if not host_value:
        raise ProxyConfigurationError(f"В прокси не указан host: {raw_line}")

    if not 1 <= port_number <= 65535:
        raise ProxyConfigurationError(f"Порт прокси вне диапазона 1..65535: {raw_line}")

    return ProxyDefinition(
        scheme=scheme,
        host=host_value,
        port=port_number,
        username=(str(username).strip() or None) if username is not None else None,
        password=(str(password).strip() or None) if password is not None else None,
        source_line=raw_line,
    )


def _validate_proxy_scheme(scheme: str) -> None:
    if scheme not in ("socks5", "socks4", "http"):
        raise ProxyConfigurationError(
            f"Поддерживаются только socks5, socks4 и http, получено: {scheme}"
        )


def load_proxies(proxy_file: Path) -> Tuple[List[ProxyDefinition], List[str]]:
    proxies: List[ProxyDefinition] = []
    invalid_lines: List[str] = []

    if not proxy_file.exists():
        raise ProxyConfigurationError(f"Файл со списком прокси не найден: {proxy_file}")

    if proxy_file.is_dir():
        raise ProxyConfigurationError(f"Указанный proxy_file является папкой, а не файлом: {proxy_file}")

    try:
        with proxy_file.open("r", encoding="utf-8-sig") as file:
            for line_number, line in enumerate(file, start=1):
                try:
                    proxy = parse_proxy_line(line)
                except ProxyConfigurationError as exc:
                    invalid_lines.append(f"Строка {line_number}: {exc}")
                    continue

                if proxy is not None:
                    proxies.append(proxy)
    except UnicodeDecodeError as exc:
        raise ProxyConfigurationError(
            f"Не удалось прочитать файл прокси {proxy_file}. Сохраните его в UTF-8."
        ) from exc
    except OSError as exc:
        raise ProxyConfigurationError(
            f"Не удалось открыть файл прокси {proxy_file}: {exc}"
        ) from exc

    return proxies, invalid_lines


class ProxyManager:
    def __init__(
        self,
        settings: ProxySettings,
        proxies: Optional[Sequence[ProxyDefinition]] = None,
        invalid_lines: Optional[Sequence[str]] = None,
    ) -> None:
        self.settings = settings
        self.proxies = list(proxies or [])
        self.invalid_lines = list(invalid_lines or [])

    @classmethod
    def from_config(cls) -> "ProxyManager":
        settings = load_proxy_settings()

        if not settings.enabled:
            return cls(settings=settings, proxies=[], invalid_lines=[])

        validate_proxy_runtime_support()
        proxies, invalid_lines = load_proxies(settings.proxy_file)
        if not proxies:
            details = ""
            if invalid_lines:
                preview = "; ".join(invalid_lines[:2])
                extra_count = len(invalid_lines) - 2
                if extra_count > 0:
                    preview = f"{preview}; еще ошибок: {extra_count}"
                details = f". Примеры ошибок: {preview}"

            raise ProxyConfigurationError(
                f"Прокси включены, но в файле {settings.proxy_file} нет валидных записей{details}"
            )

        return cls(settings=settings, proxies=proxies, invalid_lines=invalid_lines)

    @property
    def is_enabled(self) -> bool:
        return self.settings.enabled and bool(self.proxies)

    def build_plan(
        self,
        items: Sequence[Any],
        key_getter: Optional[Callable[[Any], str]] = None,
    ) -> List[ProxyAssignment]:
        items = list(items)
        key_getter = key_getter or self._default_key

        if not items:
            return []

        if not self.is_enabled:
            return [
                ProxyAssignment(
                    item=item,
                    item_key=key_getter(item),
                    order_index=index,
                    proxy=None,
                    proxy_index=None,
                    group_index=None,
                    group_position=index,
                )
                for index, item in enumerate(items)
            ]

        if self.settings.mode == "single":
            return self._build_single_plan(items, key_getter)
        if self.settings.mode == "round_robin":
            return self._build_round_robin_plan(items, key_getter)
        if self.settings.mode == "sticky_hash":
            return self._build_sticky_hash_plan(items, key_getter)

        return self._build_chunked_round_robin_plan(items, key_getter)

    def describe(self, account_count: int = 0) -> str:
        if not self.settings.enabled:
            return "Прокси отключены"

        return (
            f"{self.settings.mode_label} | "
            f"Файл: {self.settings.proxy_file} | "
            f"Прокси: {len(self.proxies)} | "
            f"Аккаунтов: {account_count}"
        )

    def write_plan(self, operation_name: str, plan: Sequence[ProxyAssignment]) -> Path:
        PLAN_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        output_path = PLAN_OUTPUT_DIR / f"{operation_name}_last_plan.json"

        summary: Dict[str, int] = {}
        if self.settings.enabled and self.proxies:
            for proxy in self.proxies:
                summary[proxy.masked_label()] = 0

        for assignment in plan:
            summary[assignment.proxy_label] = summary.get(assignment.proxy_label, 0) + 1

        payload = {
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "operation": operation_name,
            "proxy_enabled": self.settings.enabled,
            "proxy_mode": self.settings.mode,
            "proxy_mode_label": self.settings.mode_label,
            "proxy_file": str(self.settings.proxy_file),
            "proxy_count": len(self.proxies),
            "invalid_proxy_lines": list(self.invalid_lines),
            "summary": summary,
            "assignments": [
                {
                    "order": assignment.order_index + 1,
                    "item_key": assignment.item_key,
                    "proxy": assignment.proxy_label,
                    "proxy_index": assignment.proxy_index,
                    "group_index": assignment.group_index,
                    "group_position": assignment.group_position,
                }
                for assignment in plan
            ],
        }

        with output_path.open("w", encoding="utf-8") as file:
            json.dump(payload, file, indent=4, ensure_ascii=False)

        return output_path

    def _build_single_plan(
        self,
        items: Sequence[Any],
        key_getter: Callable[[Any], str],
    ) -> List[ProxyAssignment]:
        first_proxy = self.proxies[0]
        return [
            ProxyAssignment(
                item=item,
                item_key=key_getter(item),
                order_index=index,
                proxy=first_proxy,
                proxy_index=0,
                group_index=0,
                group_position=index,
            )
            for index, item in enumerate(items)
        ]

    def _build_round_robin_plan(
        self,
        items: Sequence[Any],
        key_getter: Callable[[Any], str],
    ) -> List[ProxyAssignment]:
        usage_per_proxy = [0 for _ in self.proxies]
        plan: List[ProxyAssignment] = []

        for index, item in enumerate(items):
            proxy_index = index % len(self.proxies)
            plan.append(
                ProxyAssignment(
                    item=item,
                    item_key=key_getter(item),
                    order_index=index,
                    proxy=self.proxies[proxy_index],
                    proxy_index=proxy_index,
                    group_index=proxy_index,
                    group_position=usage_per_proxy[proxy_index],
                )
            )
            usage_per_proxy[proxy_index] += 1

        return plan

    def _build_sticky_hash_plan(
        self,
        items: Sequence[Any],
        key_getter: Callable[[Any], str],
    ) -> List[ProxyAssignment]:
        usage_per_proxy = [0 for _ in self.proxies]
        plan: List[ProxyAssignment] = []

        for index, item in enumerate(items):
            item_key = key_getter(item)
            proxy_index = self._stable_proxy_index(item_key)
            plan.append(
                ProxyAssignment(
                    item=item,
                    item_key=item_key,
                    order_index=index,
                    proxy=self.proxies[proxy_index],
                    proxy_index=proxy_index,
                    group_index=proxy_index,
                    group_position=usage_per_proxy[proxy_index],
                )
            )
            usage_per_proxy[proxy_index] += 1

        return plan

    def _build_chunked_round_robin_plan(
        self,
        items: Sequence[Any],
        key_getter: Callable[[Any], str],
    ) -> List[ProxyAssignment]:
        chunk_sizes = self._build_chunk_sizes(len(items), len(self.proxies))
        groups: List[List[Tuple[Any, str, int, int]]] = []
        cursor = 0

        for proxy_index, chunk_size in enumerate(chunk_sizes):
            group: List[Tuple[Any, str, int, int]] = []
            for group_position in range(chunk_size):
                item = items[cursor]
                group.append((item, key_getter(item), proxy_index, group_position))
                cursor += 1
            groups.append(group)

        plan: List[ProxyAssignment] = []
        max_depth = max((len(group) for group in groups), default=0)

        for depth in range(max_depth):
            for group_index, group in enumerate(groups):
                if depth >= len(group):
                    continue

                item, item_key, proxy_index, group_position = group[depth]
                plan.append(
                    ProxyAssignment(
                        item=item,
                        item_key=item_key,
                        order_index=len(plan),
                        proxy=self.proxies[proxy_index],
                        proxy_index=proxy_index,
                        group_index=group_index,
                        group_position=group_position,
                    )
                )

        return plan

    @staticmethod
    def _build_chunk_sizes(item_count: int, proxy_count: int) -> List[int]:
        base_size, remainder = divmod(item_count, proxy_count)
        return [base_size + (1 if index < remainder else 0) for index in range(proxy_count)]

    @staticmethod
    def _default_key(item: Any) -> str:
        return str(item)

    def _stable_proxy_index(self, item_key: str) -> int:
        digest = hashlib.sha256(item_key.encode("utf-8")).digest()
        return int.from_bytes(digest[:4], byteorder="big") % len(self.proxies)
