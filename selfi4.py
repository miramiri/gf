from pyrogram import filters

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

# ذخیره استایل و وضعیت
user_style = {}
user_enabled = {}

def register_text_styles(app, state=None, save_state=None):
    # دستور لیست
    @app.on_message(filters.command("لیست", prefixes=".") & filters.me)
    async def list_styles(client, message):
        if len(message.command) >= 2 and message.command[1] == "متن":
            text = "📋 لیست حالت‌های متن:\n\n"
            for i, style_func in enumerate(STYLES, start=1):
                sample = style_func("نمونه متن")
                text += f"`{i}` → {sample}\n"
            text += "\n➖➖➖\nمثال: `.متن 3`\nروشن: `.متن روشن`\nخاموش: `.متن خاموش`"
            await message.reply_text(text, disable_web_page_preview=True)

    # دستور انتخاب/روشن/خاموش
    @app.on_message(filters.command("متن", prefixes=".") & filters.me)
    async def set_style(client, message):
        if len(message.command) < 2:
            await message.reply_text("❌ استفاده درست: `.متن 1` یا `.متن روشن/خاموش`")
            return

        arg = message.command[1]

        if arg == "روشن":
            user_enabled[message.from_user.id] = True
            await message.reply_text("✅ حالت متن روشن شد.")
            return
        elif arg == "خاموش":
            user_enabled[message.from_user.id] = False
            await message.reply_text("❌ حالت متن خاموش شد.")
            return

        if not arg.isdigit() or int(arg) < 1 or int(arg) > len(STYLES):
            await message.reply_text("❌ شماره نامعتبر (برای لیست: `.لیست متن`)")
            return

        user_style[message.from_user.id] = int(arg) - 1
        user_enabled[message.from_user.id] = True
        await message.reply_text(f"✅ حالت متن روی شماره {arg} تنظیم شد.")

    # تغییر متن پیام‌ها
    @app.on_message(filters.text & filters.me)
    async def stylize_message(client, message):
        if not user_enabled.get(message.from_user.id, False):
            return

        style_id = user_style.get(message.from_user.id)
        if style_id is None:
            return

        try:
            styled_text = STYLES[style_id](message.text)
        except Exception:
            styled_text = message.text

        await message.delete()
        await client.send_message(message.chat.id, styled_text)