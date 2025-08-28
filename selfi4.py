from telethon import events
import asyncio

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
    lambda t: f〰️ {t} 〰️",      # خط دار تزئینی
]

current_style = None   # استایل انتخابی
auto_edit_enabled = False  # روشن/خاموش

def register_text_styles(client, state, save_state):

    # 📑 دستور: .لیست متن
    @client.on(events.NewMessage(pattern=r"\.لیست متن$"))
    async def list_styles(event):
        if event.sender_id != state["owner_id"]:
            return
        text = "📑 لیست استایل‌ها:\n\n"
        for i, styler in enumerate(STYLES, start=1):
            sample = styler("نمونه متن")
            text += f"{i} ➝ {sample}\n"
        text += "\n📌 دستورها:\n"
        text += "`.متن n` → انتخاب استایل شماره n\n"
        text += "`.متن روشن` → روشن کردن ادیت خودکار\n"
        text += "`.متن خاموش` → خاموش کردن ادیت خودکار\n"
        await event.edit(text)

    # 🎯 دستور: .متن n
    @client.on(events.NewMessage(pattern=r"\.متن (\d+)$"))
    async def set_style(event):
        if event.sender_id != state["owner_id"]:
            return
        global current_style
        idx = int(event.pattern_match.group(1))
        if idx < 1 or idx > len(STYLES):
            return await event.edit("❌ شماره استایل نامعتبره")
        current_style = idx - 1
        await event.edit(f"✅ استایل متن روی شماره {idx} تنظیم شد")

    # 🔛 دستور: .متن روشن
    @client.on(events.NewMessage(pattern=r"\.متن روشن$"))
    async def enable_auto_edit(event):
        if event.sender_id != state["owner_id"]:
            return
        global auto_edit_enabled
        auto_edit_enabled = True
        await event.edit("✅ ادیت خودکار متن روشن شد")

    # 🔴 دستور: .متن خاموش
    @client.on(events.NewMessage(pattern=r"\.متن خاموش$"))
    async def disable_auto_edit(event):
        if event.sender_id != state["owner_id"]:
            return
        global auto_edit_enabled
        auto_edit_enabled = False
        await event.edit("🛑 ادیت خودکار متن خاموش شد")

    # 📝 اعمال خودکار استایل روی پیام‌ها
    @client.on(events.NewMessage(outgoing=True))
    async def auto_edit(event):
        global current_style, auto_edit_enabled
        if not auto_edit_enabled or current_style is None:
            return
        try:
            text = event.raw_text
            styled = STYLES[current_style](text)
            if styled != text:
                await event.edit(styled)
        except Exception as e:
            print(f"[Style Edit Error] {e}")

