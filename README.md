### Overview

Find (and optionally forward) Telegram messages from a specific folder if they match against a list of keywords.

### Prerequisites

Rename `.env.local` to `.env`, replacing the values with your own and defining the keywords you'd like the program to look for in the corresponding file.

You may be prompted to log in when you first run the program; afterwards, a `*.session` file with session info will be created and you can run the program without having to log in again.

### Usage

Run `python3 main.py`.

### CLI arguments:
1. `--dry-run`: Run without forwarding matched messages.
2. `--keep-unread`: Don't mark matched messages as read (allows you to re-run the script on the same set of messages).
3. `--log-mismatch`: Log contents of mismatched messages to `stdout`. Can be used to refine your keyword criteria.
4. `--log-match`: Log contents of matched messages to `stdout`.
5. `--check-all`: Check for matches even if the messages have been read already. Caution: might produce a lot of output.
