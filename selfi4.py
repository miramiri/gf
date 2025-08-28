from telethon import events
from telethon.tl.types import InputPeerUser

# لیست استایل‌ها
STYLES = [
    lambda t: f"**{t}**",        # 1 بولد
    lambda t: f"__{t}__",        # 2 ایتالیک
    lambda t: f"~~{t}~~",        # 3 خط خورده
    lambda t: f"`{t}`",          # 4 کد تک خطی
    lambda t: f"```{t}```",      # 5 کد چند خطی
    lambda t: f"**__{t}__**",    # 6 بولد+زیرخط
    lambda t: f"__~~{t}~~__",    # 7 زیرخط+خط خورده
    lambda t: f"**`{t}`**",      # 8 بولد+کد
    lambda t: f"✨ {t} ✨",       # 9 تزئینی
    lambda t: f"〰️ {t} 〰️",     # 10 خط دار تزئینی
]

# ذخیره استایل و وضعیت کاربر
user_style = {}
user_enabled = {}

def register_text_styles(client, state=None, save_state=None):
    
    # دستور لیست
    @client.on(events.NewMessage(pattern=r"\.لیست\s+متن"))
    async def list_styles_handler(event):
        text = "📋 لیست حالت‌های متن:\n\n"
        for i, style_func in enumerate(STYLES, start=1):
            sample = style_func("نمونه متن")
            text += f"{i} → {sample}\n"
        text += "\nمثال: `.متن 3`\nروشن: `.متن روشن`\nخاموش: `.متن خاموش`"
        await event.reply(text)
    
    # دستور انتخاب استایل یا روشن/خاموش
    @client.on(events.NewMessage(pattern=r"\.متن\s+(.+)"))
    async def set_style_handler(event):
        arg = event.pattern_match.group(1).strip()
        user_id = event.sender_id

        if arg == "روشن":
            user_enabled[user_id] = True
            await event.reply("✅ حالت متن روشن شد.")
            return
        elif arg == "خاموش":
            user_enabled[user_id] = False
            await event.reply("❌ حالت متن خاموش شد.")
            return

        if not arg.isdigit() or int(arg) < 1 or int(arg) > len(STYLES):
            await event.reply("❌ شماره نامعتبر (برای لیست: `.لیست متن`)")
            return

        user_style[user_id] = int(arg) - 1
        user_enabled[user_id] = True
        await event.reply(f"✅ حالت متن روی شماره {arg} تنظیم شد.")

    # ویرایش پیام‌ها
    @client.on(events.NewMessage)
    async def stylize_message_handler(event):
        user_id = event.sender_id
        if not user_enabled.get(user_id, False):
            return

        style_id = user_style.get(user_id)
        if style_id is None:
            return

        try:
            new_text = STYLES[style_id](event.raw_text)
        except Exception:
            new_text = event.raw_text

        # ادیت پیام فقط اگر تغییر کرده
        if new_text != event.raw_text:
            await event.delete()
            await client.send_message(event.chat_id, new_text)