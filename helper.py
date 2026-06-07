from enum import Enum
from dotenv import dotenv_values
from telethon import TelegramClient
from re import IGNORECASE, escape, search


# str derivation is needed because for some reason
# you can't directly use enum values as dict keys
# because they return tuples
class Env(str, Enum):
    NAME = ("T_NAME",)
    API_ID = ("T_API_ID",)
    API_HASH = ("T_API_HASH",)
    IGNORE_CHAR = ("T_IGNORE_CHAR",)
    FOLDER_NAME = ("T_FOLDER_NAME",)
    FWD_TO = ("T_FWD_TO",)
    KW_FILENAME = ("T_KW_FILENAME",)


cfg = dotenv_values()
client = TelegramClient(
    cfg[Env.NAME],
    cfg[Env.API_ID],
    cfg[Env.API_HASH],
)


def get_client():
    return client


def std_pos(s: str):
    return f"\033[32m{s}\033[0m"


def std_neg(s: str):
    return f"\033[33m{s}\033[0m"


def std_dire(s: str):
    return f"\033[31m{s}\033[0m"


def get_padded_match(kw, txt, p=100):
    escaped = "|".join(escape(w) for w in kw)
    return search(rf"([\s\S]{{0,{p}}})({escaped})([\s\S]{{0,{p}}})", txt, flags=IGNORECASE)
