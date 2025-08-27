from telethon import events

STYLES = {
    1: lambda t: f"**{t}**",
    2: lambda t: f"__{t}__",
    3: lambda t: f"~~{t}~~",
    4: lambda t: f"`{t}`",
    5: lambda t: f"```{t}```",
    6: lambda t: f"__**{t}**__",
    7: lambda t: f"_{t}_",
    8: lambda t: f"_**{t}**_",
    9: lambda t: f"_~~{t}~~_",
    10: lambda t: f"__**~~{t}~~**__",
}

current_style = None  # در حافظه نگهداری می‌شود

def register_text_styles(client):

    @client.on(events.NewMessage(pattern=r"\.لیست متن$"))
    async def list_styles(event):
        text = "📑 لیست استایل‌ها:\n\n"
        for k,v in STYLES.items():
            text += f"{k}- {v('نمونه متن')}\n"
        await event.edit(text)

    @client.on(events.NewMessage(pattern=r"\.متن (\d+)$"))
    async def set_style(event):
        global current_style
        idx = int(event.pattern_match.group(1))
        if idx not in STYLES:
            return await event.edit("❌ شماره استایل نامعتبره")
        current_style = idx
        await event.edit(f"✅ استایل متن روی {idx} تنظیم شد")

