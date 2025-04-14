from sys import argv
from enum import Enum
from re import search, IGNORECASE
from dotenv import dotenv_values
from telethon import TelegramClient
from telethon.tl import functions
from telethon.errors.rpcerrorlist import ChatForwardsRestrictedError
from textwrap import indent

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

class Flags(str, Enum):
		DRY_RUN = "--dry-run",
		KEEP_UNREAD = "--keep-unread",
		LOG_MISMATCH = "--log-mismatch",
		LOG_MATCH = "--log-match",
		CHECK_ALL = "--check-all",

cfg = dotenv_values()
client = TelegramClient(
		cfg[Env.NAME],
		cfg[Env.API_ID],
		cfg[Env.API_HASH],
)

def std_pos(s: str):
		return f"\033[32m{s}\033[0m"

def std_neg(s: str):
		return f"\033[33m{s}\033[0m"

async def main():
		check_all = Flags.CHECK_ALL in argv[1:]
		log_mismatch = Flags.LOG_MISMATCH in argv[1:]
		log_match = Flags.LOG_MATCH in argv[1:]
		dry_run = Flags.DRY_RUN in argv[1:]
		keep_unread = Flags.KEEP_UNREAD in argv[1:]
		total_messages, total_chats, matches = 0, 0, 0

		KEYWORDS = []
		IGNORE = []

		with open(cfg[Env.KW_FILENAME]) as file:
			for line in file:
					if line[0] == cfg[Env.IGNORE_CHAR]:
							IGNORE.append(line.rstrip()[1:])
					else:
							KEYWORDS.append(line.rstrip())
		
		# first get the ids of chats that belong to a specific folder
		# then filter all chats based on this list (such is the structure of the API)
		request = (await client(functions.messages.GetDialogFiltersRequest())).to_dict()
		folder = next(
				(folder for folder in request.get("filters") if folder.get("title", {}).get("text") == cfg[Env.FOLDER_NAME]),
				None,
		)
		chat_ids = [chat["channel_id"] for chat in folder["include_peers"]]

		async for chat in client.iter_dialogs():
			if chat.entity.id in chat_ids and (chat.unread_count != 0 or check_all):
					for msg in await client.get_messages(chat, chat.unread_count):
						if not msg.text:
							continue
						elif (match := search("|".join(KEYWORDS), msg.text, IGNORECASE)) and not search("|".join(IGNORE), msg.text, IGNORECASE):
								matches += 1
								print(f'{std_pos("match:")} "{match.group()}" @ "{chat.name}"')
								
								if log_match:
									print(indent(msg.text, " " * 4))

								if dry_run:
									continue
								
								try:
										await client.forward_messages(cfg[Env.FWD_TO], msg)
								except ChatForwardsRestrictedError:
										await client.send_message(cfg[Env.FWD_TO], msg.text)
						elif log_mismatch:
								print(f"\n{std_neg("mismatch:")}\n", indent(msg.text, " " * 4), end="\n")
						
						total_messages += 1
					
					if not keep_unread:
						await client.send_read_acknowledge(chat)

					total_chats += 1
		
		print(f"\n{std_pos(str(matches))} matches among {std_neg(str(total_messages))} messages within {total_chats} chats")

if __name__ == "__main__":
		with client:
				client.loop.run_until_complete(main())
