from pyrogram import Client
import asyncio

with open('/home/lunkwill/projects/lemmy_auto_icon/secrets/telegram_app_id.txt', 'r') as file:
    app_id = file.read().strip()

with open('/home/lunkwill/projects/lemmy_auto_icon/secrets/telegram_app_hash.txt', 'r') as file:
    api_hash = file.read().strip()

async def send_telegram_text_as_me_to_bot(message):
    app = Client("my_account2", api_id=app_id, api_hash=api_hash)
    async with app:
        await app.send_message("lunkstealth_bot", message)

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
coro = send_telegram_text_as_me_to_bot("Lemmy art has been updated.")
loop.run_until_complete(coro)
