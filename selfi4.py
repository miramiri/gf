# -*- coding: utf-8 -*-
from telethon import events

def register_text_styles(client, state, save_state):

    # استایل‌ها با HTML (پایدارتر از md)
    STYLES = {
        1: lambda t: f"<b>{t}</b>",                 # بولد
        2: lambda t: f"<u>{t}</u>",                 # زیرخط
        3: lambda t: f"<s>{t}</s>",                 # خط‌خورده
        4: lambda t: f"<code>{t}</code>",           # تک‌کد
        5: lambda t: f"<pre>{t}</pre>",             # بلاک‌کد
        6: lambda t: f"<b><u>{t}</u></b>",          # بولد + زیرخط
    }

    # نمایش لیست استایل‌ها
    @client.on(events.NewMessage(pattern=r"^\s*[\.\/!]?\s*لیست\s+متن\s*$"))
    async def show_styles(event):
        if event.sender_id != state.get("owner_id"): 
            return
        txt = "📑 لیست استایل‌های موجود:\n\n"
        for i in sorted(STYLES.keys()):
            sample = STYLES[i]("نمونه متن")
            txt += f"{i}. {sample}\n"
        txt += "\nبا دستور `.متن <شماره>` انتخاب کن."
        await event.reply(txt, parse_mode="html")

    # انتخاب استایل
    @client.on(events.NewMessage(pattern=r"^\s*[\.\/!]?\s*متن\s+(\d+)\s*$"))
    async def set_style(event):
        if event.sender_id != state.get("owner_id"):
            return
        try:
            num = int(event.pattern_match.group(1))
        except:
            return await event.reply("❌ شماره نامعتبره.")
        if num not in STYLES:
            return await event.reply("❌ شماره اشتباهه.")
        state["text_style"] = num
        if callable(save_state):
            save_state()
        await event.reply(f"✅ استایل شماره {num} فعال شد.")

    # اعمال استایل روی پیام‌های خودت
    @client.on(events.NewMessage)
    async def apply_style(event):
        # فقط پیام‌های خود اکانت
        if event.sender_id != state.get("owner_id"):
            return
        # دستورها رو دست نزن
        raw = event.raw_text or ""
        if not raw or raw.strip().startswith("."):
            return
        style_num = state.get("text_style")
        if not style_num:
            return
        fn = STYLES.get(style_num)
        if not fn:
            return
        try:
            new_text = fn(raw)
            await event.edit(new_text, parse_mode="html")
        except Exception as e:
            print(f"⚠️ خطا در apply_style: {e}")

