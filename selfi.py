import asyncio
import json
import os
from telethon import TelegramClient, events, Button
from flask import Flask
from threading import Thread

from autocatch import register_autocatch
from selfi2 import register_extra_cmds   # دستورات جدا (لیست/آیدی/بلاک/تاریخ/تنظیم)

from games import register_games
from menu import register_menu
from group_manager import register_group_manager
from sargarmi_plus import register_sargarmi_plus
from security import register_security
from help1 import register_help1
from sargarmi import register_sargarmi
from sell import register_sell
from selfi4 import register_text_styles
from clock import register_clock
from backup_manager import register_backup_manager

# --- سرور keep_alive برای ریپلیت ---
app = Flask('')

@app.route('/')
def home():
    return "نيما نوب سگ!"

def run():
    app.run(host="0.0.0.0", port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- خواندن API_ID و API_HASH ---
with open("confing.json", "r", encoding="utf-8") as f:
    config = json.load(f)
API_ID = int(config["api_id"])
API_HASH = config["api_hash"]

SESSIONS = [
    "acc", "acc1", "acc2", "acc3", "acc4",
    "acc5", "acc6", "acc7", "acc8", "acc9"
]

# فایل مشترک برای گروه‌ها (شناسه‌های تلگرام)
GROUPS_FILE = "groups.json"
if os.path.exists(GROUPS_FILE):
    with open(GROUPS_FILE, "r", encoding="utf-8") as f:
        GLOBAL_GROUPS = json.load(f)
else:
    GLOBAL_GROUPS = []
    with open(GROUPS_FILE, "w", encoding="utf-8") as f:
        json.dump(GLOBAL_GROUPS, f)

def save_groups():
    with open(GROUPS_FILE, "w", encoding="utf-8") as f:
        json.dump(GLOBAL_GROUPS, f, ensure_ascii=False, indent=2)

async def setup_client(session_name):
    DATA_FILE = f"data_{session_name}.json"
    state = {
    "owner_id": None,
    "echo_users": [],
    "enabled": True,
    "delay": 2.0,
    "stop_emoji": ["⚜", "💮", "⚡", "❓"],  
    "last_user": None,
    "last_group": None,
    "funny_text": "نیما فشاری 😂",
    "status_msg_id": None,
    "auto_groups": [],     
    "copy_plus_user": None,   # کاربر انتخابی برای کپی پلاس
    "clock_on": False,        # 🔥 اضافه شد
    "clock_font": 1,          # 🔥 اضافه شد
    "text_style": None        # 🔥 اضافه شد
}

    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                saved = json.load(f)
            state.update(saved)
        except Exception:
            pass

    def save_state():
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, indent=2)

    client = TelegramClient(session_name, API_ID, API_HASH)
    await client.start()

    me = await client.get_me()
    if not state["owner_id"]:
        state["owner_id"] = me.id
        save_state()
        print(f"✅ [{session_name}] Owner set: {me.id}")
    else:
        print(f"✅ [{session_name}] Started")

    def is_owner(e): 
        return e.sender_id == state["owner_id"]

    # ---------- متن منو وضعیت
    def _status_text():
        return (
            f"🤖 وضعیت ربات {session_name}\n"
            f"═════════════════════════\n"
            f"🔹 وضعیت:\n"
            f"   ✅ فعال: {'بله' if state['enabled'] else 'خیر'}\n"
            f"   ⏳ تاخیر: {state['delay']} ثانیه\n"
            f"   🔄 کاربران کپی: {len(state['echo_users'])}\n"
            f"   ⛔ ایموجی قطع‌کننده: {', '.join(state['stop_emoji']) if state['stop_emoji'] else 'هیچ'}\n"
            f"   🟢 گروه‌های اتوکچ (این اکانت): {len(state['auto_groups'])}\n"
            f"   🟣 گروه‌های کپی (عمومی): {len(GLOBAL_GROUPS)}\n"
            f"\n"
            f"📖 دستورات موجود:\n"
            f"   👤 مدیریت کاربران:\n"
            f"      • .کپی (ریپلای)\n"
            f"      • .کپی خاموش (ریپلای)\n"
            f"      • .کپی پلاس (ریپلای)\n"
            f"      • .لیست\n"
            f"   ⚙️ مدیریت ربات:\n"
            f"      • .ریست دیتا\n"
            f"      • .عدد (مثل .0.5)\n"
            f"      • .تنظیم [متن]\n"
            f"      • .ست 😀 💮 ⚡️\n"
            f"      • .ست حذف همه\n"
            f"   🛡 مدیریت گروه/کاربر:\n"
            f"      • .ثبت / .حذف\n"
            f"      • .ثبت کپی\n"
            f"      • .بلاک (ریپلای یا آیدی)\n"
            f"      • .آیدی (ریپلای)\n"
            f"   📅 ابزارها:\n"
            f"      • .تاریخ\n"
        )

    async def send_status():
        try:
            text = _status_text()
            if state.get("status_msg_id"):
                msg = await client.get_messages("me", ids=state["status_msg_id"])
                if msg:
                    await msg.edit(text)
                    return
            sent = await client.send_message("me", text)
            state["status_msg_id"] = sent.id
            save_state()
        except Exception as e:
            print(f"⚠️ خطا در ارسال وضعیت: {e}")

    await send_status()

    # ---------- تغییر تاخیر با '.0.5' و ...
    @client.on(events.NewMessage(pattern=r"\.(\d+(?:\.\d+)?)$"))
    async def set_delay(event):
        if not is_owner(event): return
        try:
            delay = float(event.pattern_match.group(1))
        except Exception:
            return
        state["delay"] = delay
        save_state()
        await event.edit(f"⏳ تاخیر روی {delay} ثانیه تنظیم شد.")
        await send_status()

    # ---------- کپی / کپی خاموش
    @client.on(events.NewMessage(pattern=r".کپی$"))
    async def enable_copy(event):
        if not is_owner(event): return
        if not event.is_reply:
            await event.edit("❌ روی پیام ریپلای کن!")
            return
        reply = await event.get_reply_message()
        user = await reply.get_sender()
        if user.id not in state["echo_users"]:
            state["echo_users"].append(user.id)
            state["last_user"] = user.id
            state["last_group"] = event.chat_id
            save_state()
            await event.edit(f"✅ کپی برای {user.first_name} فعال شد.")
        else:
            await event.edit("ℹ️ قبلاً فعال بود.")
        await send_status()

    @client.on(events.NewMessage(pattern=r".کپی خاموش$"))
    async def disable_copy(event):
        if not is_owner(event): return
        if not event.is_reply:
            await event.edit("❌ روی پیام ریپلای کن!")
            return
        reply = await event.get_reply_message()
        user = await reply.get_sender()
        if user.id in state["echo_users"]:
            state["echo_users"].remove(user.id)
            save_state()
            await event.edit(f"⛔ کپی برای {user.first_name} خاموش شد.")
        else:
            await event.edit("ℹ️ این کاربر فعال نبود.")
        await send_status()

    # ---------- کپی پلاس
    @client.on(events.NewMessage(pattern=r".کپی پلاس$"))
    async def copy_plus(event):
        if not is_owner(event): return
        if not event.is_reply:
            await event.edit("❌ روی پیام ریپلای کن!")
            return
        reply = await event.get_reply_message()
        user = await reply.get_sender()
        state["copy_plus_user"] = user.id
        save_state()
        await event.edit(
            f"✨ کپی پلاس فعال شد برای {user.first_name}\n"
            f"هر وقت اتوکچ قطع شد، دوباره براش فعال میشه.",
            buttons=[[Button.inline("❌ حذف کپی پلاس", b"del_copy_plus")]]
        )
        await send_status()

    @client.on(events.CallbackQuery(pattern=b"del_copy_plus"))
    async def del_copy_plus(event):
        if not is_owner(event): return
        state["copy_plus_user"] = None
        save_state()
        await event.edit("❌ کپی پلاس حذف شد.")
        await send_status()

    # ---------- ریست دیتا
    @client.on(events.NewMessage(pattern=r".ریست دیتا$"))
    async def reset_data(event):
        if not is_owner(event): return
        state.clear()
        state.update({
            "owner_id": event.sender_id,
            "echo_users": [],
            "enabled": True,
            "delay": 2.0,
            "stop_emoji": ["⚜", "💮", "⚡", "❓"],
            "last_user": None,
            "last_group": None,
            "funny_text": "مگه نیما فشاری 😂",
            "status_msg_id": state.get("status_msg_id"),
            "auto_groups": [],
                        "copy_plus_user": None
        })
        save_state()
        await event.edit("♻️ فایل دیتا ریست شد.")
        await send_status()

    # ---------- ثبت / حذف گروه 
    @client.on(events.NewMessage(pattern=r".ثبت(?:\s+کپی)?$"))
    async def register_group(event):
        if not is_owner(event): return
        if not event.is_group:
            await event.edit("❌ فقط در گروه کار می‌کند.")
            return
        gid = event.chat_id
        if gid not in GLOBAL_GROUPS:
            GLOBAL_GROUPS.append(gid)
            save_groups()
        if "کپی" in event.raw_text:
            if gid not in state["copy_groups"]:
                state["copy_groups"].append(gid)
            text = "✅عاقبت."
        else:
            if gid not in state["auto_groups"]:
                state["auto_groups"].append(gid)
            text = "گروه به بلک لیست اضافه شد."
        save_state()
        await event.edit(text)
        await send_status()

    @client.on(events.NewMessage(pattern=r".حذف$"))
    async def unregister_group(event):
        if not is_owner(event): return
        if not event.is_group:
            await event.edit("❌ فقط در گروه کار می‌کند.")
            return
        gid = event.chat_id
        if gid in GLOBAL_GROUPS:
            GLOBAL_GROUPS.remove(gid)
            save_groups()
        if gid in state["auto_groups"]:
            state["auto_groups"].remove(gid)
        if gid in state["copy_groups"]:
            state["copy_groups"].remove(gid)
        save_state()
        await event.edit("⛔ گروه حذف شد.")
        await send_status()

    # ---------- دستور .ست
    @client.on(events.NewMessage(pattern=r".ست حذف همه$"))
    async def clear_stop_emoji(event):
        if not is_owner(event): return
        state["stop_emoji"] = []
        save_state()
        await event.edit("🧹 ایموجی‌های قطع‌کننده حذف شد.")
        await send_status()

    @client.on(events.NewMessage(pattern=r".ست$"))
    async def show_stop_emoji(event):
        if not is_owner(event): return
        cur = ", ".join(state["stop_emoji"]) if state["stop_emoji"] else "هیچ"
        await event.edit(f"⛔ ایموجی‌های فعلی: {cur}\n"
                         f"برای تنظیم چندتا باهم: `.ست 😀 💮 ⚡️`")

    @client.on(events.NewMessage(pattern=r".ست (.+)$"))
    async def set_stop_emoji(event):
        if not is_owner(event): return
        args = event.pattern_match.group(1).strip()
        tokens = [tok for tok in args.split() if tok]
        seen = set()
        emojis = []
        for t in tokens:
            if t not in seen:
                seen.add(t)
                emojis.append(t)
        if len(emojis) > 10:
            emojis = emojis[:10]
        state["stop_emoji"] = emojis
        save_state()
        cur = ", ".join(state["stop_emoji"]) if state["stop_emoji"] else "هیچ"
        await event.edit(f"✅ ایموجی‌های قطع‌کننده تنظیم شد: {cur}")
        await send_status()

    # ---------- موتور کپی
    @client.on(events.NewMessage)
    async def echo(event):
        if not state["enabled"]:
            return
        if event.chat_id not in GLOBAL_GROUPS:
            return
        if event.sender_id in state["echo_users"]:
            await asyncio.sleep(state["delay"])
            try:
                if event.media:
                    await client.send_file(event.chat_id, event.media, caption=event.text)
                else:
                    await client.send_message(event.chat_id, event.text)
            except Exception as e:
                print(f"⚠️ خطا در کپی: {e}")

    # ---------- ماژول‌ها
    register_autocatch(client, state, GLOBAL_GROUPS, save_state, send_status)
    register_extra_cmds(client, state, GLOBAL_GROUPS, save_state, send_status)
    register_games(client, state, GLOBAL_GROUPS, save_state, send_status)
    register_menu(client, state, GLOBAL_GROUPS, save_state, send_status)
    register_group_manager(client, state, GLOBAL_GROUPS, save_state, send_status)
    register_sargarmi_plus(client, state, GLOBAL_GROUPS, save_state, send_status)  # سرگرمی پیشرفته
    register_security(client, state, GLOBAL_GROUPS, save_state, send_status)
    register_help1(client, state, GLOBAL_GROUPS, save_state, send_status)
    register_sargarmi(client, state, GLOBAL_GROUPS, save_state, send_status)  # سرگرمی ساده
    register_sell(client)
    register_text_styles(client, state, save_state)
    register_clock(client, state, save_state)
    register_backup_manager(client, state)

    return client



async def main():
    client_list = await asyncio.gather(*[setup_client(s) for s in SESSIONS])
    print(f"🚀 {len(client_list)} کلاینت ران شد.")

    # دیکشنری برای دسترسی به نام acc ها
    clients = {}
    for idx, c in enumerate(client_list):
        if idx == 0:
            clients["acc"] = c
        else:
            clients[f"acc{idx}"] = c

OWNER_ID = 7768586264

@clients["acc"].on(events.NewMessage(pattern=r"^(acc(?:\d+| all))\s+(.+)$"))
@clients["acc"].on(events.MessageEdited(pattern=r"^(acc(?:\d+| all))\s+(.+)$"))
async def control_accounts(event):
    if event.sender_id != OWNER_ID:
        return

    target = event.pattern_match.group(1)   # acc1 یا acc all
    command = event.pattern_match.group(2)  # مثلا .بکاپ یا .کپی

    # اگر ریپلای بود
    reply = None
    if await event.get_reply_message():
        reply = await event.get_reply_message()

    if target == "acc all":
        for name, cl in clients.items():
            await run_command(cl, command, reply)
        await event.reply(f"📡 دستور برای همه اکانت‌ها اجرا شد: {command}")
    else:
        if target in clients:
            await run_command(clients[target], command, reply)
            await event.reply(f"📡 دستور برای {target} اجرا شد: {command}")
        else:
            await event.reply("❌ همچین کلاینتی وصل نیست.")


async def run_command(client, command, reply=None):
    """
    این تابع دستور رو مستقیم روی کلاینت اجرا میکنه
    """
    # حالت خاص برای کپی
    if command.startswith(".کپی") and reply:
        user_id = reply.sender_id
        # دیتا بیس مخصوص این کلاینت رو لود کن
        db_file = f"data_{client.session.filename}.json"
        import json, os
        data = {}
        if os.path.exists(db_file):
            data = json.load(open(db_file, "r", encoding="utf-8"))
        if "copy_list" not in data:
            data["copy_list"] = []
        if user_id not in data["copy_list"]:
            data["copy_list"].append(user_id)
        json.dump(data, open(db_file, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        await client.send_message("me", f"✅ {user_id} به لیست کپی اضافه شد.")
        return

    # حالت عادی → پیام فیک بساز و هندلرها رو صدا بزن
    fake_event = events.NewMessage.Event(
        message=type("msg", (), {"message": command, "sender_id": OWNER_ID, "is_private": True}),
        chat=None,
        client=client
    )
    for handler in client.list_event_handlers():
        if isinstance(handler[0], events.NewMessage):
            await handler[1](fake_event)

if __name__ == "__main__":
    keep_alive()   # 🔥 اضافه شد برای روشن موندن توی Replit
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())

