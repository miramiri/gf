from pyrogram import Client, filters

# لیست استایل‌ها
STYLES = [
    lambda t: f"**{t}**",        # بولد
    lambda t: f"__{t}__",        # ایتالیک
    lambda t: f"~~{t}~~",        # خط خورده
    lambda t: f"`{t}`",          # کد تک خطی
    lambda t: f"```{t}```",      # کد چند خطی
    lambda t: f"**__{t}__**",    # بولد+زیرخط
    lambda t: f"__~~{t}~~__",    # زیرخط+خط خورده
    lambda t: f"**`{t}`**",      # بولد+کد
    lambda t: f"✨ {t} ✨",       # تزئینی
    lambda t: f"〰️ {t} 〰️",     # خط دار تزئینی
]

# ذخیره استایل و وضعیت هر کاربر
user_style = {}
user_enabled = {}

app = Client("my_bot", api_id=12345, api_hash="your_api_hash", bot_token="your_bot_token")


# لیست استایل‌ها
@app.on_message(filters.command("لیست", prefixes=".") & filters.me)
async def list_styles(client, message):
    if len(message.command) >= 2 and message.command[1] == "متن":
        text = "📋 لیست حالت‌های متن:\n\n"
        for i, style_func in enumerate(STYLES, start=1):
            sample = style_func("نمونه متن")
            text += f"`{i}` → {sample}\n"
        text += "\n➖➖➖\nمثال: `.متن 3`\nروشن: `.متن روشن`\nخاموش: `.متن خاموش`"
        await message.reply_text(text, disable_web_page_preview=True)


# تغییر حالت متن
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


# ویرایش پیام‌های کاربر
@app.on_message(filters.text & filters.me)
async def stylize_message(client, message):
    if not user_enabled.get(message.from_user.id, False):
        return

    style_id = user_style.get(message.from_user.id)
    if style_id is None:
        return

    text = message.text
    try:
        styled_text = STYLES[style_id](text)
    except Exception:
        styled_text = text

    await message.delete()
    await client.send_message(message.chat.id, styled_text)


app.run()
