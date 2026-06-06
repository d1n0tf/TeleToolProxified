from importlib import import_module


_EXPORTS = {
    "session_analyzer_info": (".session_analyzer_info", "session_analyzer_info"),
    "create_session_qr": (".create_session_qrcode", "create_session_qr"),
    "create_session_code": (".create_session_code", "create_session_code"),
    "account_info_save_info": (".get_account_info", "account_info_save_info"),
    "session_to_tdata_convert": (".convert_session_tdata", "session_to_tdata_convert"),
    "tdata_to_session_convert": (".convert_tadata_session", "tdata_to_session_convert"),
    "count_dialogs": (".clener_dialogs", "count_dialogs"),
    "clean_dialogs": (".clener_dialogs", "clean_dialogs"),
}

__all__ = list(_EXPORTS)


def __getattr__(name):
    if name not in _EXPORTS:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

    module_name, attr_name = _EXPORTS[name]
    module = import_module(module_name, __name__)
    value = getattr(module, attr_name)
    globals()[name] = value
    return value
