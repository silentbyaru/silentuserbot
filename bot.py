from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.errors import ChatWriteForbiddenError
import os
import asyncio
import json
import threading
from fastapi import FastAPI
import uvicorn

# 🔹 Start FastAPI health server for Koyeb
app = FastAPI()

@app.get("/")
async def root():
    return {"status": "Bot is alive!"}

def run_web():
    uvicorn.run(app, host="0.0.0.0", port=8080)

threading.Thread(target=run_web, daemon=True).start()

# 🔹 Telegram Credentials
API_ID = 29140356
API_HASH = "f5976eb15ac17891076075f76a9c312b"
SESSION = "1BVtsOJwBuyYUXilH3FxsxE_ZSlQ-CeCot2riJlpLIkPcu-9Goh6BDmbe3yGyTuVwPvId2cykZrb-SpbBGL2BSkRl1uQJtuGsZXpZememvBt6NlRoIt-_LED1nRTH72ZXHHKQmCAiIRmKjrJu_nxSsx_DGCSG3BGx8IwHOyBCShtxgzBsro82wBqVhnQWi3ZJbEAN_d6F9kaCUzKQi_EOtlUt4ODdpthbmBzi1GRy6E_ZyCVR5FbwDfqTsFESfmh0xbhGwIN8Muum-1fFd-JHWDC_pnrmIL_8iFoU0TNwkxClPRVq9Jj1_rZnbd-Zjm6erPfTncohNypRHvT396T5eP8mDI_WgWc="

ADMINS = [6046055058]
GROUPS_FILE = "groups.json"
SETTINGS_FILE = "settings.json"

# 🔹 Load Saved Data
def load_data():
    try:
        with open(GROUPS_FILE, "r") as f:
            groups = set(json.load(f))
    except:
        groups = set()

    try:
        with open(SETTINGS_FILE, "r") as f:
            data = json.load(f)
            reply_msg = data.get("reply_msg", "SEARCH YOUR MOVIE HERE @Yourmovielinkk")
            delete_delay = data.get("delete_delay", 15)
    except:
        reply_msg = "SEARCH YOUR MOVIE HERE @Yourmovielinkk"
        delete_delay = 15

    return groups, reply_msg, delete_delay

# 🔹 Save functions
def save_groups(groups):
    with open(GROUPS_FILE, "w") as f:
        json.dump(list(groups), f)

def save_settings(reply_msg, delete_delay):
    with open(SETTINGS_FILE, "w") as f:
        json.dump({"reply_msg": reply_msg, "delete_delay": delete_delay}, f)

# 🔹 Load group and message settings
TARGET_GROUPS, AUTO_REPLY_MSG, DELETE_DELAY = load_data()
client = TelegramClient(StringSession(SESSION), API_ID, API_HASH)

# 🔹 Auto-reply to group messages
@client.on(events.NewMessage)
async def handler(event):
    global DELETE_DELAY
    try:
        if event.chat_id in TARGET_GROUPS and event.sender_id != (await client.get_me()).id:
            sent_msg = await event.reply(AUTO_REPLY_MSG)
            if DELETE_DELAY > 0:
                await asyncio.sleep(DELETE_DELAY)
                try:
                    await sent_msg.delete()
                except Exception as e:
                    print(f"[!] Couldn't delete message: {e}")
    except ChatWriteForbiddenError:
        print(f"[!] Cannot write in {event.chat_id}, bot might be restricted.")
    except Exception as e:
        print(f"[!] Unhandled error: {e}")

# 🔹 /add command to add group ID
@client.on(events.NewMessage(pattern="/add"))
async def add_group(event):
    if event.sender_id in ADMINS:
        try:
            group_id = int(event.message.text.split(" ", 1)[1])
            TARGET_GROUPS.add(group_id)
            save_groups(TARGET_GROUPS)
            await event.reply(f"✅ Added group: `{group_id}`")
        except:
            await event.reply("❌ Error: Provide a valid group ID.")

# 🔹 /remove command to remove group ID
@client.on(events.NewMessage(pattern="/remove"))
async def remove_group(event):
    if event.sender_id in ADMINS:
        try:
            group_id = int(event.message.text.split(" ", 1)[1])
            TARGET_GROUPS.discard(group_id)
            save_groups(TARGET_GROUPS)
            await event.reply(f"❎ Removed group: `{group_id}`")
        except:
            await event.reply("❌ Error: Provide a valid group ID.")

# 🔹 /setmsg command to update auto-reply message
@client.on(events.NewMessage(pattern="/setmsg"))
async def set_msg(event):
    global AUTO_REPLY_MSG, DELETE_DELAY
    if event.sender_id in ADMINS:
        try:
            AUTO_REPLY_MSG = event.message.text.split(" ", 1)[1]
            save_settings(AUTO_REPLY_MSG, DELETE_DELAY)
            await event.reply("✅ Reply message updated!")
        except:
            await event.reply("❌ Error: Provide a message.")

# 🔹 /delmsg command to clear auto-reply message
@client.on(events.NewMessage(pattern="/delmsg"))
async def del_msg(event):
    global AUTO_REPLY_MSG, DELETE_DELAY
    if event.sender_id in ADMINS:
        AUTO_REPLY_MSG = ""
        save_settings(AUTO_REPLY_MSG, DELETE_DELAY)
        await event.reply("🗑️ Auto reply message cleared.")

# 🔹 /setdel command to change delete delay
@client.on(events.NewMessage(pattern="/setdel"))
async def set_del(event):
    global DELETE_DELAY, AUTO_REPLY_MSG
    if event.sender_id in ADMINS:
        try:
            seconds = int(event.message.text.split(" ", 1)[1])
            DELETE_DELAY = max(0, seconds)
            save_settings(AUTO_REPLY_MSG, DELETE_DELAY)
            await event.reply(f"⏱️ Auto-delete time set to {DELETE_DELAY} seconds.")
        except:
            await event.reply("❌ Error: Provide a number of seconds.")

# 🔹 Start bot
async def main():
    print("🤖 Bot is running...")
    await client.run_until_disconnected()

client.start()
client.loop.run_until_complete(main())
