
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
    lambda t: f"〰️ {t} 〰️",     # 10 خط‌دار تزئینی
]

# وضعیت و استایل
owner_enabled = False
owner_styles = []
_last_texts = {}  # جلوگیری از لوپ ادیت

def register_text_styles(client, state=None, save_state=None):

    def is_owner(e):
        if not state:
            return False
        return e.sender_id == state.get("owner_id")

    # دستور لیست استایل‌ها
    @client.on(events.NewMessage(pattern=r"\.لیست\s+متن$"))
    async def list_styles_handler(event):
        if not is_owner(event):
            return
        text = "📋 لیست حالت‌های متن:\n\n"
        for i, style_func in enumerate(STYLES, start=1):
            sample = style_func("نمونه متن")
            text += f"{i} → {sample}\n"
        text += "\nمثال: `.متن 1 3 9`\nخاموش: `.متن خاموش`"
        await event.edit(text)

    # دستور انتخاب استایل یا خاموش
    @client.on(events.NewMessage(pattern=r"\.متن\s+(.+)"))
    async def set_style_handler(event):
        global owner_enabled, owner_styles   # ← اصلاح شد
        if not is_owner(event):
            return

        arg = event.pattern_match.group(1).strip()

        if arg == "خاموش":
            owner_enabled = False
            owner_styles = []
            await event.edit("❌ حالت متن خاموش شد.")
            return

        parts = arg.split()
        styles = []
        for p in parts:
            if not p.isdigit() or int(p) < 1 or int(p) > len(STYLES):
                await event.edit(f"❌ شماره نامعتبر: {p} (برای لیست: `.لیست متن`)")
                return
            styles.append(int(p) - 1)

        owner_styles = styles
        owner_enabled = True
        await event.edit(f"✅ حالت متن روی شماره {', '.join(parts)} فعال شد.")

    # اِعمال استایل روی پیام‌های owner (جدید + ادیت)
    @client.on(events.NewMessage)
    @client.on(events.MessageEdited)
    async def stylize_owner_messages(event):
        if not is_owner(event):
            return
        if not owner_enabled or not owner_styles:
            return

        msg_id = event.message.id
        current_text = event.text or ""

        # جلوگیری از لوپ
        if _last_texts.get(msg_id) == current_text:
            return

        new_text = current_text
        try:
            for style_id in owner_styles:
                new_text = STYLES[style_id](new_text)
        except Exception:
            return

        if new_text != current_text:
            await event.edit(new_text)
            _last_texts[msg_id] = new_text
