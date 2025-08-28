from telethon import events

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

# آیدی owner
owner_id = 123456789  # <-- اینو با آیدی تلگرام خودت عوض کن

# وضعیت و استایل owner
owner_enabled = True
owner_styles = []  # لیست شماره استایل‌ها برای ترکیب

def register_text_styles(client, state=None, save_state=None):

    # دستور لیست
    @client.on(events.NewMessage(pattern=r"\.لیست\s+متن"))
    async def list_styles_handler(event):
        if event.sender_id != owner_id:
            return
        text = "📋 لیست حالت‌های متن:\n\n"
        for i, style_func in enumerate(STYLES, start=1):
            sample = style_func("نمونه متن")
            text += f"{i} → {sample}\n"
        text += "\nمثال: `.متن 1 3 9`\nروشن: `.متن روشن`\nخاموش: `.متن خاموش`"
        await event.reply(text)

    # دستور انتخاب استایل یا روشن/خاموش
    @client.on(events.NewMessage(pattern=r"\.متن\s+(.+)"))
    async def set_style_handler(event):
        nonlocal owner_enabled, owner_styles
        if event.sender_id != owner_id:
            return

        arg = event.pattern_match.group(1).strip()

        if arg == "روشن":
            owner_enabled = True
            await event.reply("✅ حالت متن روشن شد.")
            return
        elif arg == "خاموش":
            owner_enabled = False
            await event.reply("❌ حالت متن خاموش شد.")
            return

        # ترکیب استایل‌ها: جدا شده با space
        parts = arg.split()
        styles = []
        for p in parts:
            if not p.isdigit() or int(p) < 1 or int(p) > len(STYLES):
                await event.reply(f"❌ شماره نامعتبر: {p} (برای لیست: `.لیست متن`)")
                return
            styles.append(int(p)-1)

        owner_styles = styles
        owner_enabled = True
        await event.reply(f"✅ حالت متن روی شماره {', '.join(parts)} تنظیم شد.")

    # ادیت پیام‌های owner
    @client.on(events.MessageEdited)
    async def stylize_edit_handler(event):
        if event.sender_id != owner_id:
            return
        if not owner_enabled or not owner_styles:
            return

        text = event.text
        try:
            for style_id in owner_styles:
                text = STYLES[style_id](text)
        except Exception:
            pass

        # فقط ادیت کن اگر تغییر کرده
        if text != event.text:
            await event.edit(text)