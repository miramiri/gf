from pyrogram import Client, filters

# ذخیره حالت متن هر کاربر
user_styles = {}
user_enabled = {}

# لیست حالت‌ها
styles = {
    "1": ("bold", "**نمونه متن**"),
    "2": ("italic", "__نمونه متن__"),
    "3": ("strike", "~~نمونه متن~~"),
    "4": ("code", "`نمونه متن`"),
    "5": ("underline", "__نمونه متن__"),   # زیرخط
    "6": ("spoiler", "||نمونه متن||"),     # اسپویلر
    "7": ("link", "[نمونه متن](https://google.com)")  # لینک
}

app = Client("my_bot", api_id=12345, api_hash="your_api_hash", bot_token="your_bot_token")


# دستور لیست حالت‌ها
@app.on_message(filters.command("لیست", prefixes=".") & filters.me)
async def list_styles(client, message):
    if len(message.command) >= 2 and message.command[1] == "متن":
        text = "📋 لیست حالت‌های متن:\n\n"
        for num, (name, example) in styles.items():
            text += f"`{num}` → {name}\n{example}\n\n"
        text += "➖➖➖\nمثال تغییر: `.متن 3`\nروشن/خاموش: `.متن روشن` یا `.متن خاموش`"
        await message.reply_text(text, disable_web_page_preview=True)


# دستور انتخاب حالت یا روشن/خاموش
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

    if arg not in styles:
        await message.reply_text("❌ عدد درست بده (برای دیدن لیست: `.لیست متن`)")
        return

    user_styles[message.from_user.id] = arg
    user_enabled[message.from_user.id] = True
    await message.reply_text(f"✅ حالت متن روی `{styles[arg][0]}` تنظیم شد.")


# تغییر پیام‌های کاربر
@app.on_message(filters.text & filters.me)
async def stylize_message(client, message):
    if not user_enabled.get(message.from_user.id, False):
        return

    style_id = user_styles.get(message.from_user.id)
    if not style_id:
        return

    text = message.text
    if style_id == "1":   # bold
        new_text = f"**{text}**"
    elif style_id == "2": # italic
        new_text = f"__{text}__"
    elif style_id == "3": # strike
        new_text = f"~~{text}~~"
    elif style_id == "4": # code
        new_text = f"`{text}`"
    elif style_id == "5": # underline
        new_text = f"__{text}__"
    elif style_id == "6": # spoiler
        new_text = f"||{text}||"
    elif style_id == "7": # link
        new_text = f"[{text}](https://google.com)"
    else:
        new_text = text

    await message.delete()
    await client.send_message(message.chat.id, new_text, disable_web_page_preview=True)


app.run()
