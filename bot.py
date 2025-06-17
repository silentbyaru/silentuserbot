from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.errors import ChatWriteForbiddenError, SessionPasswordNeededError
import os
import asyncio
import json
import threading
import time
from fastapi import FastAPI
import uvicorn

# 🔹 Health check for Koyeb
app = FastAPI()
@app.get("/")
async def root():
    return {"status": "Bot is alive!"}

def run_web():
    uvicorn.run(app, host="0.0.0.0", port=8080)

threading.Thread(target=run_web, daemon=True).start()

# 🔹 Telegram credentials
API_ID = 22938364
API_HASH = "81cc7882c88b7cb7785cb1a8d59e93a8"
SESSION = "1BVtsOJwBu5k4CQuf64FEA73FBWCkTimy2HECd4lMcbWEiXIwc8gGrCwcZs2gCCzRZ6L995oZpkvQ4qicCFpxaA5giPsq0cQ3BGRx0JNcZABTT2iFIz57_FlX1gq1gOQ9hEnf6-WcuexDYQ-0oWuf5xGN1yZ3Eqh2QcAThPGKeXLfQQpjVcq_hYpIjPETCUvy1DboNd8iKS4l4skUbfPGH3tJ4274-fkj-nc0AGRfvxJuJFyD8sGSE9shwlcrqzKCflmgH5Imdb6u2XrYjiVV0aOaomq_maiMUtaqKJXrjSlhV909cMjfqr2s9VfjA4ZQAnJJUFlSDOqnd-Hc834wdY4KLad4VYo="

ADMINS = [6046055058]
GROUPS_FILE = "groups.json"
SETTINGS_FILE = "settings.json"

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
            reply_gap = data.get("reply_gap", 30)
    except:
        reply_msg = "SEARCH YOUR MOVIE HERE @Yourmovielinkk"
        delete_delay = 15
        reply_gap = 30

    return groups, reply_msg, delete_delay, reply_gap

def save_groups(groups):
    with open(GROUPS_FILE, "w") as f:
        json.dump(list(groups), f)

def save_settings(reply_msg, delete_delay, reply_gap):
    with open(SETTINGS_FILE, "w") as f:
        json.dump({"reply_msg": reply_msg, "delete_delay": delete_delay, "reply_gap": reply_gap}, f)

TARGET_GROUPS, AUTO_REPLY_MSG, DELETE_DELAY, REPLY_GAP = load_data()
client = TelegramClient(StringSession(SESSION), API_ID, API_HASH)
last_reply_time = {}

@client.on(events.ChatAction)
async def auto_add_group_on_join(event):
    if event.user_joined or event.user_added:
        me = await client.get_me()
        if event.user_id == me.id and event.is_group:
            TARGET_GROUPS.add(event.chat_id)
            save_groups(TARGET_GROUPS)
            print(f"[+] Auto-added group: {event.chat_id}")

@client.on(events.NewMessage)
async def handler(event):
    global DELETE_DELAY, REPLY_GAP
    try:
        sender = await event.get_sender()
        if (
            event.chat_id in TARGET_GROUPS and
            event.sender_id != (await client.get_me()).id and
            not getattr(sender, 'bot', False)
        ):
            now = time.time()
            last = last_reply_time.get(event.chat_id, 0)

            if now - last < REPLY_GAP:
                return

            last_reply_time[event.chat_id] = now
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

@client.on(events.NewMessage(pattern="/setmsg"))
async def set_msg(event):
    global AUTO_REPLY_MSG, DELETE_DELAY, REPLY_GAP
    if event.sender_id in ADMINS:
        try:
            AUTO_REPLY_MSG = event.message.text.split(" ", 1)[1]
            save_settings(AUTO_REPLY_MSG, DELETE_DELAY, REPLY_GAP)
            await event.reply("✅ Reply message updated!")
        except:
            await event.reply("❌ Error: Provide a message.")

@client.on(events.NewMessage(pattern="/delmsg"))
async def del_msg(event):
    global AUTO_REPLY_MSG, DELETE_DELAY, REPLY_GAP
    if event.sender_id in ADMINS:
        AUTO_REPLY_MSG = ""
        save_settings(AUTO_REPLY_MSG, DELETE_DELAY, REPLY_GAP)
        await event.reply("🗑️ Auto reply message cleared.")

@client.on(events.NewMessage(pattern="/setdel"))
async def set_del(event):
    global DELETE_DELAY, AUTO_REPLY_MSG, REPLY_GAP
    if event.sender_id in ADMINS:
        try:
            seconds = int(event.message.text.split(" ", 1)[1])
            DELETE_DELAY = max(0, seconds)
            save_settings(AUTO_REPLY_MSG, DELETE_DELAY, REPLY_GAP)
            await event.reply(f"⏱️ Auto-delete time set to {DELETE_DELAY} seconds.")
        except:
            await event.reply("❌ Error: Provide a number of seconds.")

@client.on(events.NewMessage(pattern="/setgap"))
async def set_gap(event):
    global REPLY_GAP, DELETE_DELAY, AUTO_REPLY_MSG
    if event.sender_id in ADMINS:
        try:
            seconds = int(event.message.text.split(" ", 1)[1])
            REPLY_GAP = max(0, seconds)
            save_settings(AUTO_REPLY_MSG, DELETE_DELAY, REPLY_GAP)
            await event.reply(f"⏳ Time gap between replies set to {REPLY_GAP} seconds.")
        except:
            await event.reply("❌ Error: Provide a number of seconds.")

@client.on(events.NewMessage(pattern="/id"))
async def id_command(event):
    if event.is_group or event.is_channel:
        chat = await event.get_chat()
        await event.reply(
            f"🆔 Group Info:\n"
            f"👥 Group Name: {chat.title}\n"
            f"📢 Chat ID: `{event.chat_id}`\n"
            f"👤 Your User ID: `{event.sender_id}`"
        )
    else:
        await event.reply(f"👤 This is a private chat.\nYour ID: `{event.sender_id}`")

@client.on(events.NewMessage(pattern="/gensession"))
async def generate_session(event):
    if event.is_private and event.sender_id in ADMINS:
        await event.reply("📲 Send me your phone number in international format (e.g. +919876543210)")
        
        try:
            phone_event = await client.wait_for(events.NewMessage(from_users=event.sender_id), timeout=60)
            phone = phone_event.message.message.strip()

            temp_client = TelegramClient(StringSession(), API_ID, API_HASH)
            await temp_client.connect()

            await temp_client.send_code_request(phone)
            await event.respond("🔐 Enter the OTP (numbers only):")

            code_event = await client.wait_for(events.NewMessage(from_users=event.sender_id), timeout=60)
            code = code_event.message.message.strip().replace(" ", "")

            try:
                await temp_client.sign_in(phone, code)
            except SessionPasswordNeededError:
                await event.respond("🔑 This account has 2-Step Verification enabled.\nPlease enter your password:")
                pwd_event = await client.wait_for(events.NewMessage(from_users=event.sender_id), timeout=60)
                password = pwd_event.message.message.strip()
                await temp_client.sign_in(password=password)

            string = temp_client.session.save()
            await client.send_message(event.sender_id, f"✅ Here is your session string:\n\n`{string}`\n\n⚠️ **Keep it safe. Do not share it with anyone!**")

        except Exception as e:
            await event.respond(f"❌ Failed to generate session: {e}")
        finally:
            await temp_client.disconnect()

# 🔹 Start bot
async def main():
    print("🤖 Bot is running...")
    await client.run_until_disconnected()

client.start()
client.loop.run_until_complete(main())
