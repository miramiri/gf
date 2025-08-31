# controller.py
import re
from telethon import events

# آیدی مدیر مرکزی (تغییر بده به آیدی خودت)
ADMIN_ID = 7768586264

def register_controller(controller_client, CLIENTS, STATES, STATUS_FUNCS):
    """
    controller_client: یکی از کلاینت‌ها که دستورها را گوش می‌دهد
    CLIENTS: dict[str, TelegramClient]
    STATES: dict[str, dict]
    STATUS_FUNCS: dict[str, callable]
    """

    def is_admin(e):
        return e.sender_id == ADMIN_ID

    def has(s):
        return s in CLIENTS and s in STATES

    async def status_text(s):
        st = STATES[s]
        return (
            f"📟 {s}\n"
            f"— فعال: {'✅' if st.get('enabled', True) else '❌'}\n"
            f"— Delay پیام: {st.get('echo_delay', 2.0)} ثانیه\n"
            f"— Delay کچ: {st.get('catch_delay', 3.0)} ثانیه\n"
            f"— کاربران اکو: {len(st.get('echo_users', []))}\n"
            f"— گروه‌های کچ: {len(st.get('auto_groups', []))}\n"
        )

    # لیست اکانت‌ها
    @controller_client.on(events.NewMessage(pattern=r"^\.اکانت‌ها$"))
    async def list_sessions(event):
        if not is_admin(event): return
        lines = []
        for s in CLIENTS:
            st = STATES[s]
            lines.append(
                f"• {s} ┇ {'✅' if st['enabled'] else '❌'} ┇ ⏳echo:{st['echo_delay']}s catch:{st['catch_delay']}s"
            )
        await event.reply("\n".join(lines) or "چیزی ثبت نشده.")

    # وضعیت یک اکانت
    @controller_client.on(events.NewMessage(pattern=r"^\.وضعیت\s+(\S+)$"))
    async def show_status(event):
        if not is_admin(event): return
        s = event.pattern_match.group(1)
        if not has(s): return await event.reply("سشن پیدا نشد.")
        await event.reply(await status_text(s))

    # فعال/غیرفعال
    @controller_client.on(events.NewMessage(pattern=r"^\.فعال\s+(\S+)$"))
    async def enable_session(event):
        if not is_admin(event): return
        s = event.pattern_match.group(1)
        if not has(s): return await event.reply("سشن نامعتبر.")
        STATES[s]["enabled"] = True
        await event.reply(f"✅ {s} فعال شد.")
        await STATUS_FUNCS[s]()

    @controller_client.on(events.NewMessage(pattern=r"^\.غیرفعال\s+(\S+)$"))
    async def disable_session(event):
        if not is_admin(event): return
        s = event.pattern_match.group(1)
        if not has(s): return await event.reply("سشن نامعتبر.")
        STATES[s]["enabled"] = False
        await event.reply(f"⛔ {s} غیرفعال شد.")
        await STATUS_FUNCS[s]()

    # تنظیم delay پیام‌ها (فقط عدد خالی مثل ".5" یا "1.2")
    @controller_client.on(events.NewMessage(pattern=r"^[0-9]+(?:\.[0-9]+)?$"))
    async def set_echo_delay(event):
        if not is_admin(event): return
        val = float(event.raw_text)
        # روی همه اکانت‌ها اعمال می‌شود
        for s in STATES:
            STATES[s]["echo_delay"] = val
            await STATUS_FUNCS[s]()
        await event.reply(f"⏳ Echo-Delay همه اکانت‌ها روی {val}s تنظیم شد.")

    # تنظیم delay کچ (.کچ 5)
    @controller_client.on(events.NewMessage(pattern=r"^\.کچ\s+([0-9]+(?:\.[0-9]+)?)$"))
    async def set_catch_delay(event):
        if not is_admin(event): return
        val = float(event.pattern_match.group(1))
        for s in STATES:
            STATES[s]["catch_delay"] = val
            await STATUS_FUNCS[s]()
        await event.reply(f"⏳ Catch-Delay همه اکانت‌ها روی {val}s تنظیم شد.")

    # افزودن کاربر echo با ریپلای
    @controller_client.on(events.NewMessage(pattern=r"^\.کپی\+\s+(\S+)$"))
    async def copy_plus(event):
        if not is_admin(event): return
        if not event.is_reply: return await event.reply("روی پیام کاربر ریپلای کن.")
        s = event.pattern_match.group(1)
        if not has(s): return await event.reply("سشن نامعتبر.")
        rep = await event.get_reply_message()
        u = await rep.get_sender()
        lst = STATES[s].setdefault("echo_users", [])
        if u.id not in lst:
            lst.append(u.id)
            await event.reply(f"✅ کاربر {u.id} اضافه شد به echo {s}")
        else:
            await event.reply("ℹ️ از قبل در لیست بود.")
        await STATUS_FUNCS[s]()

    @controller_client.on(events.NewMessage(pattern=r"^\.کپی-\s+(\S+)$"))
    async def copy_minus(event):
        if not is_admin(event): return
        if not event.is_reply: return await event.reply("روی پیام کاربر ریپلای کن.")
        s = event.pattern_match.group(1)
        if not has(s): return await event.reply("سشن نامعتبر.")
        rep = await event.get_reply_message()
        u = await rep.get_sender()
        lst = STATES[s].setdefault("echo_users", [])
        if u.id in lst:
            lst.remove(u.id)
            await event.reply(f"⛔ کاربر {u.id} حذف شد از echo {s}")
        else:
            await event.reply("ℹ️ در لیست نبود.")
        await STATUS_FUNCS[s]()

    # ارسال پیام از اکانت
    @controller_client.on(events.NewMessage(pattern=r"^\.ارسال\s+(\S+)\s+(-?\d+)\s+(.+)$"))
    async def send_from(event):
        if not is_admin(event): return
        s, chat_id, text = event.pattern_match.group(1), int(event.pattern_match.group(2)), event.pattern_match.group(3)
        if not has(s): return await event.reply("سشن نامعتبر.")
        await CLIENTS[s].send_message(chat_id, text)
        await event.reply(f"📤 ارسال شد از {s} به {chat_id}")

    # داشبورد
    @controller_client.on(events.NewMessage(pattern=r"^\.داشبورد$"))
    async def dashboard(event):
        if not is_admin(event): return
        out = [await status_text(s) for s in CLIENTS]
        await event.reply("\n".join(out) if out else "چیزی نیست.")