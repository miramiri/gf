from telethon import events

STYLES = {
    1: lambda t: f"**{t}**",          # بولد
    2: lambda t: f"__{t}__",          # زیرخط
    3: lambda t: f"~~{t}~~",          # خط‌خورده
    4: lambda t: f"`{t}`",            # تک‌کد
    5: lambda t: f"```{t}```",        # بلاک‌کد
    6: lambda t: f"__**{t}**__",      # بولد + زیرخط
    7: lambda t: f"_{t}_",            # ایتالیک
    8: lambda t: f"_**{t}**_",        # ایتالیک + بولد
    9: lambda t: f"_~~{t}~~_",        # ایتالیک + خط‌خورده
    10: lambda t: f"__**~~{t}~~**__", # بولد + زیرخط + خط‌خورده
}
def register_text_styles(client, state, save_state):

    @client.on(events.NewMessage(pattern=r"\.لیست متن$"))
    async def list_styles(event):
        if event.sender_id != state["owner_id"]: return
        text = "📑 لیست استایل‌ها:\n\n"
        for k,v in STYLES.items():
            text += f"{k}- {v('نمونه متن')}\n"
        await event.edit(text)

    @client.on(events.NewMessage(pattern=r"\.متن (\d+)$"))
    async def set_style(event):
        if event.sender_id != state["owner_id"]: return
        idx = int(event.pattern_match.group(1))
        if idx not in STYLES:
            return await event.edit("❌ شماره استایل نامعتبره")
        state["text_style"] = idx
        save_state()
        await event.edit(f"✅ استایل متن روی {idx} تنظیم شد")

