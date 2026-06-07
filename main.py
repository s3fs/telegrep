from asyncio import sleep as asleep
from random import randint
from sys import argv
from enum import Enum
from dotenv import dotenv_values
from telethon.tl import functions
from telethon.errors.rpcerrorlist import FloodWaitError, MessageTooLongError
from helper import get_client, Env, get_padded_match, std_pos, std_neg
from difflib import SequenceMatcher
from datetime import datetime

INFO_PREFIX = "[INFO]"
MATCH_PAD = 100

class Flags(str, Enum):
    DRY_RUN = ("--dry-run",)
    KEEP_UNREAD = ("--keep-unread",)
    LOG_MISMATCH = ("--log-mismatch",)
    LOG_MATCH = ("--log-match",)
    CHECK_ALL = ("--check-all",)


cfg = dotenv_values()
client = get_client()


async def main():
    check_all = Flags.CHECK_ALL in argv[1:]
    log_mismatch = Flags.LOG_MISMATCH in argv[1:]
    # log_match = Flags.LOG_MATCH in argv[1:] # always log matches for now
    dry_run = Flags.DRY_RUN in argv[1:]
    keep_unread = Flags.KEEP_UNREAD in argv[1:]
    total_messages, total_chats, matches, duplicates = 0, 0, 0, 0

    KEYWORDS = []
    IGNORE = []
    prev_msgs = []
    mismatches = []

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
        (
            folder
            for folder in request.get("filters")
            if folder.get("title", {}).get("text") == cfg[Env.FOLDER_NAME]
        ),
        None,
    )
    chat_ids = [chat["channel_id"] for chat in folder["include_peers"]]


    async for chat in client.iter_dialogs():
        if chat.entity.id in chat_ids and (chat.unread_count != 0 or check_all):
            print(f"{std_pos(INFO_PREFIX)} Checking {chat.name} ({chat.entity.id})...")
            for msg in await client.get_messages(chat, chat.unread_count):
                link = f"https://t.me/c/{chat.entity.id}/{msg.id}"

                if not msg.text:
                    print(f"{std_neg(INFO_PREFIX)} No text in message ({link})", msg)
                    continue

                # skip messages similar to ones that we've already encountered
                if any(
                    rat := SequenceMatcher(None, prev_msg, msg.text).ratio() > 0.6
                    for prev_msg in prev_msgs
                ):
                    print(
                        f"{std_neg(INFO_PREFIX)} Message {rat * 100}% similar to the one already encountered"
                    )
                    duplicates += 1
                    continue
                else:
                    prev_msgs.append(msg.text)

                match = get_padded_match(KEYWORDS, msg.text, MATCH_PAD)
                mismatch = get_padded_match(IGNORE, msg.text, MATCH_PAD)
                payload = f"{msg.text}\n\n({link})"

                if match and not mismatch:
                    matches += 1

                    print(f"{std_pos('match:')} ...{match.group()}... @ {chat.name}")

                    if dry_run:
                        continue
                    try:
                        await client.send_message(
                            int(cfg[Env.FWD_TO]),
                            payload,
                        )
                        await asleep(randint(1, 2))
                    except FloodWaitError as e:
                        await asleep(e.seconds + randint(1, 5))
                        await client.send_message(
                            int(cfg[Env.FWD_TO]),
                            payload,
                        )
                    except MessageTooLongError:
                        print(f"{std_neg(INFO_PREFIX)} Message too long:", payload)
                elif log_mismatch and mismatch:
                    print(
                        f"{std_neg('mismatch:')} ...{mismatch.group()}... @ {chat.name} ({link})"
                    )
                    mismatches.append(payload)

                total_messages += 1

            if not keep_unread:
                await client.send_read_acknowledge(chat)

            total_chats += 1

    with open(f"logs/{datetime.now().isoformat()}", "a") as file:
        file.write("%%%".join(mismatches))
    print(
        f"\n{std_pos(str(matches))} matches among {std_neg(str(total_messages))} messages within {total_chats} chats, including {std_neg(str(duplicates))} duplicates"
    )


if __name__ == "__main__":
    with client:
        client.loop.run_until_complete(main())
