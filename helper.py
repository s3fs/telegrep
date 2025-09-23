from enum import Enum
from dotenv import dotenv_values
from telethon import TelegramClient

# str derivation is needed because for some reason
# you can't directly use enum values as dict keys
# because they return tuples
class Env(str, Enum):
		NAME = "T_NAME",
		API_ID = "T_API_ID",
		API_HASH = "T_API_HASH",
		IGNORE_CHAR = "T_IGNORE_CHAR",
		FOLDER_NAME = "T_FOLDER_NAME",
		FWD_TO = "T_FWD_TO",
		KW_FILENAME = "T_KW_FILENAME",

cfg = dotenv_values()
client = TelegramClient(
		cfg[Env.NAME],
		cfg[Env.API_ID],
		cfg[Env.API_HASH],
)

def get_client():
    return client
