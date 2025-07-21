# FULL MODIFIED CODE
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.errors import ChatWriteForbiddenError
import os, asyncio, json, threading, time
from fastapi import FastAPI
import uvicorn
import logging

logging.basicConfig(level=logging.INFO, filename="error.log", filemode="a",
                    format="%(asctime)s - %(levelname)s - %(message)s")

app = FastAPI()
@app.get("/")
async def root():
    return {"status": "Bot is alive!"}
threading.Thread(target=lambda: uvicorn.run(app, host="0.0.0.0", port=8080), daemon=True).start()

# Bot 1
API_ID1 = 29192127
API_HASH1 = "daa07f15fbc89fb7f4fb4c363032bed4"
SESSION1 = "1BVtsOJwBuzE5tVCioLWj1__c90fsNDl_9DKZipYggvPTWPrdpvlux6sOKJnN6WdFErwK1_uyso3JGqJbP67tbFFLhSX_Pa1BnrfuQ_ennkf3MDRBGoDWsQ95TKw9ZjSm1XoiYLxoGGC0tsVIuDqHfWdjaAvxEOOOrAZD7N6RDlH-aLsnTehlvfmTWynT9b5GNUwpHfSEHcwF95uuj5syOvYbBMbZA2PmDiMiRhKdd_g1LVkhGwx7w6siURm2921t0APlQ4WlXs36o07VaxZbuFz4LjdJ7rIF4ISvBhlchXdHVMjUNtFRwzHShjnlIRnB_-nHkol4SAIqGk_gDqXo-b1t3D9cMrc="
ADMIN1 = 7952514019

# Bot 2
API_ID2 = 27611770
API_HASH2 = "6950f9a1b53b3453e745bc893b28e54d"
SESSION2 = "1BVtsOJwBu6F7FrsiOb8yoVywFkyBMP7LN0lKMzEoCNh8ktejVXEZ_N9SI5NSwhjfs5kvK0evDX1sD9CZKuhR7lPzztR9xpuWeOLJmXT1Bc2m3_fD7ZDnurZwed6KEDlB7Yu45gFn8PUcNsti43ePIa8_0Kt6TUGgMQ28AFdeZeFaudwvxOJYYXu8oZphYPTNufYCoPQvXWLJlQPKrK96lmyi5GRNCx-c9fz80CuQZWjkkfKjfkVoAUZV1cnY0unsb1nTig-vrLChHVbthlH6QimL_RsL3Y3jXGX7kD3Wl9v2BAm_hFo5A7VqUipNKf8TD9Xz7UBRAZ9MS7lZufrWS9vV9kSAZII="
ADMIN2 = 8024038960

# Files
GROUPS_FILE1 = "groups1.json"
SETTINGS_FILE1 = "settings1.json"
GROUPS_FILE2 = "groups2.json"
SETTINGS_FILE2 = "settings2.json"

def load_data(groups_file, settings_file, default_msg):
    try: groups = set(json.load(open(groups_file)))
    except: groups = set()
    try:
        d = json.load(open(settings_file))
        return (
            groups,
            d.get("reply_msg", default_msg),
            d.get("delete_delay", 15),
            d.get("reply_gap", 30),
            d.get("pm_msg", None)
        )
    except: return groups, default_msg, 15, 30, None

def save_groups(path, groups): json.dump(list(groups), open(path, "w"))
def save_settings(path, msg, d, g, pm_msg): json.dump({"reply_msg": msg, "delete_delay": d, "reply_gap": g, "pm_msg": pm_msg}, open(path, "w"))

groups1, msg1, delay1, gap1, pm_msg1 = load_data(GROUPS_FILE1, SETTINGS_FILE1, "🤖 Bot1 here!")
groups2, msg2, delay2, gap2, pm_msg2 = load_data(GROUPS_FILE2, SETTINGS_FILE2, "👥 Bot2 here!")
last_reply1, last_reply2 = {}, {}

client1 = TelegramClient(StringSession(SESSION1), API_ID1, API_HASH1)
client2 = TelegramClient(StringSession(SESSION2), API_ID2, API_HASH2)

# Group auto-reply handlers
@client1.on(events.NewMessage)
async def bot1_handler(event):
    try:
        if event.is_private and pm_msg1:
            m = await event.reply(pm_msg1)
            await asyncio.sleep(60); await m.delete()
        elif event.chat_id in groups1 and not event.sender.bot:
            now = time.time()
            if now - last_reply1.get(event.chat_id, 0) < gap1: return
            last_reply1[event.chat_id] = now
            m = await event.reply(msg1)
            if delay1 > 0: await asyncio.sleep(delay1); await m.delete()
    except ChatWriteForbiddenError: pass
    except Exception as e: logging.error(f"[Bot1] {e}")

@client2.on(events.NewMessage)
async def bot2_handler(event):
    try:
        if event.is_private and pm_msg2:
            m = await event.reply(pm_msg2)
            await asyncio.sleep(60); await m.delete()
        elif event.chat_id in groups2 and not event.sender.bot:
            now = time.time()
            if now - last_reply2.get(event.chat_id, 0) < gap2: return
            last_reply2[event.chat_id] = now
            m = await event.reply(msg2)
            if delay2 > 0: await asyncio.sleep(delay2); await m.delete()
    except ChatWriteForbiddenError: pass
    except Exception as e: logging.error(f"[Bot2] {e}")

# Admin Bot1
@client1.on(events.NewMessage)
async def bot1_admin(e):
    global msg1, delay1, gap1, pm_msg1
    if e.sender_id != ADMIN1: return
    txt = e.raw_text.strip()
    if e.is_private:
        if txt.startswith("/addgroup"):
            try: gid = int(txt.split(" ",1)[1])
            except: return await e.reply("❌ Usage: /addgroup -100xxxx")
            groups1.add(gid); save_groups(GROUPS_FILE1, groups1); return await e.reply(f"✅ Added {gid}")
        elif txt.startswith("/removegroup"):
            try: gid = int(txt.split(" ",1)[1])
            except: return await e.reply("❌ Usage: /removegroup -100xxxx")
            groups1.discard(gid); save_groups(GROUPS_FILE1, groups1); return await e.reply(f"❌ Removed {gid}")
        elif txt.startswith("/setmsgpm "):
            pm_msg1 = txt.split(" ", 1)[1]; save_settings(SETTINGS_FILE1, msg1, delay1, gap1, pm_msg1)
            return await e.reply("✅ PM auto-reply set.")
        elif txt == "/setmsgpmoff":
            pm_msg1 = None; save_settings(SETTINGS_FILE1, msg1, delay1, gap1, pm_msg1)
            return await e.reply("❌ PM auto-reply turned off.")
    if txt == "/add": groups1.add(e.chat_id); save_groups(GROUPS_FILE1, groups1); return await e.reply("✅ Group added.")
    elif txt == "/remove": groups1.discard(e.chat_id); save_groups(GROUPS_FILE1, groups1); return await e.reply("❌ Group removed.")
    elif txt.startswith("/setmsg "): msg1 = txt.split(" ",1)[1]; save_settings(SETTINGS_FILE1, msg1, delay1, gap1, pm_msg1); await e.reply("✅ Message set")
    elif txt.startswith("/setdel "): delay1 = int(txt.split(" ",1)[1]); save_settings(SETTINGS_FILE1, msg1, delay1, gap1, pm_msg1); await e.reply("✅ Delete delay set")
    elif txt.startswith("/setgap "): gap1 = int(txt.split(" ",1)[1]); save_settings(SETTINGS_FILE1, msg1, delay1, gap1, pm_msg1); await e.reply("✅ Gap set")
    elif txt == "/status":
        await e.reply(f"Groups: {len(groups1)}\nMsg: {msg1}\nPM msg: {pm_msg1 or '❌ Off'}\nDel: {delay1}s\nGap: {gap1}s")
    elif txt == "/ping": await e.reply("🏓 Bot1 alive!")

# Admin Bot2
@client2.on(events.NewMessage)
async def bot2_admin(e):
    global msg2, delay2, gap2, pm_msg2
    if e.sender_id != ADMIN2: return
    txt = e.raw_text.strip()
    if e.is_private:
        if txt.startswith("/addgroup"):
            try: gid = int(txt.split(" ",1)[1])
            except: return await e.reply("❌ Usage: /addgroup -100xxxx")
            groups2.add(gid); save_groups(GROUPS_FILE2, groups2); return await e.reply(f"✅ Added {gid}")
        elif txt.startswith("/removegroup"):
            try: gid = int(txt.split(" ",1)[1])
            except: return await e.reply("❌ Usage: /removegroup -100xxxx")
            groups2.discard(gid); save_groups(GROUPS_FILE2, groups2); return await e.reply(f"❌ Removed {gid}")
        elif txt.startswith("/setmsgpm "):
            pm_msg2 = txt.split(" ", 1)[1]; save_settings(SETTINGS_FILE2, msg2, delay2, gap2, pm_msg2)
            return await e.reply("✅ PM auto-reply set.")
        elif txt == "/setmsgpmoff":
            pm_msg2 = None; save_settings(SETTINGS_FILE2, msg2, delay2, gap2, pm_msg2)
            return await e.reply("❌ PM auto-reply turned off.")
    if txt == "/add": groups2.add(e.chat_id); save_groups(GROUPS_FILE2, groups2); return await e.reply("✅ Group added.")
    elif txt == "/remove": groups2.discard(e.chat_id); save_groups(GROUPS_FILE2, groups2); return await e.reply("❌ Group removed.")
    elif txt.startswith("/setmsg "): msg2 = txt.split(" ",1)[1]; save_settings(SETTINGS_FILE2, msg2, delay2, gap2, pm_msg2); await e.reply("✅ Message set")
    elif txt.startswith("/setdel "): delay2 = int(txt.split(" ",1)[1]); save_settings(SETTINGS_FILE2, msg2, delay2, gap2, pm_msg2); await e.reply("✅ Delete delay set")
    elif txt.startswith("/setgap "): gap2 = int(txt.split(" ",1)[1]); save_settings(SETTINGS_FILE2, msg2, delay2, gap2, pm_msg2); await e.reply("✅ Gap set")
    elif txt == "/status":
        await e.reply(f"Groups: {len(groups2)}\nMsg: {msg2}\nPM msg: {pm_msg2 or '❌ Off'}\nDel: {delay2}s\nGap: {gap2}s")
    elif txt == "/ping": await e.reply("🏓 Bot2 alive!")

# Start both bots
async def start_clients():
    try: await client1.start()
    except Exception as e: logging.error(f"[Client1] {e}")
    try: await client2.start()
    except Exception as e: logging.error(f"[Client2] {e}")
    tasks = []
    if client1.is_connected(): tasks.append(client1.run_until_disconnected())
    if client2.is_connected(): tasks.append(client2.run_until_disconnected())
    print("✅ Running bots...")
    if tasks: await asyncio.gather(*tasks)
    else: print("❌ Both clients failed.")

asyncio.get_event_loop().run_until_complete(start_clients())
