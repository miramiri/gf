import asyncio
from datetime import datetime
from telethon import events
from telethon.tl.functions.account import UpdateProfileRequest


# لیست فونت‌ها
FONTS = [
    "𝟶𝟶:𝟶𝟶",
    "𝟘𝟘:𝟘𝟘",
    "⓪⓪:⓪⓪",
    "⓪⓪:⓪⓪",
    "⓿⓿:⓿⓿",
    "𝟢𝟢:𝟢𝟢",
    "𝟬𝟬:𝟬𝟬",
    "𝟎𝟎:𝟎𝟎",
    "００:００",
    "₀₀:₀₀",
    "⁰⁰:⁰⁰",
    "⓪⓪:⓪⓪",
    "𝟶𝟶:𝟶𝟶",
    "҉0҉0҉:҉0҉0҉",
    "0‌0:0‌0",
    "0‌0:0‌0",
    "0‌0:0‌0",
    "♥0♥0♥:♥0♥0♥",
    "≋0≋0≋:≋0≋0≋",
    "░0░0░:░0░0░",
    "⊶0⊶0⊶:⊶0⊶0⊶",
    "⊰0⊱0⊰:⊱0⊱0⊱",
    "⦅0⦆0⦅:⦆0⦆0⦆",
    "⦑0⦒0⦑:⦒0⦒0⦒",
    "⧼0⧽0⧼:⧽0⧽0⧽",
    "⨀0⨀0⨀:⨀0⨀0⨀",
    "⨌0⨌0⨌:⨌0⨌0⨌",
    "⩴0⩴0⩴:⩴0⩴0⩴",
    "⪉0⪉0⪉:⪉0⪉0⪉",
    "⫶0⫶0⫶:⫶0⫶0⫶",
    "⬘0⬘0⬘:⬘0⬘0⬘",
    "⬚0⬚0⬚:⬚0⬚0⬚",
    "⬦0⬦0⬦:⬦0⬦0⬦",
    "⬧0⬧0⬧:⬧0⬧0⬧",
    "⬨0⬨0⬨:⬨0⬨0⬨",
    "╚0╝0╚:╝0╚0╝",
    "╠0╣0╠:╣0╠0╣",
    "『0』『0』『:』『0』『0』",
    "【0】【0】【:】【0】【0】",
    "〖0〗0〖:〗0〖0〗",
    "〘0〙0〘:〙0〙0〙",
    "〚0〛0〚:〛0〛0〛",
    "〝0〞0〝:〞0〞0〞",
    "〟0〟0〟:〟0〟0〟",
    "﹅0﹆0﹅:﹆0﹆0﹆",
    "﹉0﹊0﹉:﹊0﹊0﹊",
    "﹋0﹌0﹋:﹌0﹌0﹌",
    "﹎0﹏0﹎:﹏0﹏0﹏",
    "﹐0﹑0﹐:﹑0﹑0﹑",
    "﹔0﹕0﹔:﹕0﹕0﹕",
    "﹖0﹗0﹖:﹗0﹗0﹗",
    "﹙0﹚0﹙:﹚0﹚0﹚",
]


def register_clock(client, state, save_state):

    async def update_lastname():
        while True:
            if state.get("clock_on", False):
                try:
                    now = datetime.now().strftime("%H:%M")
                    font_index = state.get("clock_font", 1) - 1
                    if 0 <= font_index < len(FONTS):
                        template = FONTS[font_index]
                    else:
                        template = "00:00"
                    formatted = template.replace("0", now[0]).replace("0", now[1], 1).replace("0", now[3]).replace("0", now[4], 1)
                    me = await client.get_me()
                    await client(UpdateProfileRequest(
                        first_name=me.first_name or "",
                        last_name=formatted
                    ))
                    print(f"⏰ [{me.id}] ساعت پروفایل آپدیت شد: {formatted}")
                except Exception as e:
                    print("⚠️ خطا در آپدیت ساعت:", e)
            await asyncio.sleep(60)

    client.loop.create_task(update_lastname())

    # روشن/خاموش کردن ساعت
    @client.on(events.NewMessage(pattern=r"\.ساعت (روشن|خاموش)$"))
    async def toggle_profile_clock(event):
        if event.sender_id != state["owner_id"]:
            return
        arg = event.pattern_match.group(1)
        if arg == "روشن":
            state["clock_on"] = True
            await event.edit("✅ ساعت پروفایل روشن شد.")
        else:
            state["clock_on"] = False
            await event.edit("⛔ ساعت پروفایل خاموش شد.")
        save_state()

    # تغییر فونت
    @client.on(events.NewMessage(pattern=r"\.ساعت فونت (\d+)$"))
    async def set_clock_font(event):
        if event.sender_id != state["owner_id"]:
            return
        num = int(event.pattern_match.group(1))
        if 1 <= num <= len(FONTS):
            state["clock_font"] = num
            save_state()
            await event.edit(f"🔤 فونت ساعت روی {num} تنظیم شد.")
        else:
            await event.edit("❌ شماره فونت نامعتبر است (۱ تا ۵۲).")

    # لیست ساعت
    @client.on(events.NewMessage(pattern=r"\.لیست ساعت$"))
    async def clock_list(event):
        if event.sender_id != state["owner_id"]:
            return
        msg = """ıllıllııllıllııllıllııllıllııllıllııllıllııllıllııllıllııllı
🕰️ ساعت 
══════●═══════════════
✧ .ساعت ⤳ (روشن یا خاموش)

🔄 وضعیت ساعت
———————————————
✧ .ساعت فونت ⤳ (1 ... 52)

🔤 تنظیم فونت
———————————————
—————fonts—————
""" + "\n".join([f"{i+1}- {f}" for i, f in enumerate(FONTS)])
        await event.edit(msg)