from telethon import events
from helper import get_client

client = get_client()

@client.on(events.NewMessage)
async def observe(event):
    print(event.stringify())

client.start()
client.run_until_disconnected()
