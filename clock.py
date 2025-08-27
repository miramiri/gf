import asyncio
from datetime import datetime
import pytz
from telethon import events, functions

# 📌 منطقه زمانی ایران (بندرعباس = تهران)
IRAN_TZ = pytz.timezone("Asia/Tehran")

# لیست فونت‌ها (1..52)
FONTS = [
    "𝟶𝟶:𝟶𝟶", "𝟘𝟘:𝟘𝟘", "⓪⓪:⓪⓪", "⓪⓪:⓪⓪", "⓿⓿:⓿⓿", "𝟢𝟢:𝟢𝟢",
    "𝟬𝟬:𝟬𝟬", "𝟎𝟎:𝟎𝟎", "００:００", "₀₀:₀₀", "⁰⁰:⁰⁰", "⓪⓪:⓪⓪",
    "𝟶𝟶:𝟶𝟶", "҉0҉0҉:҉0҉0҉", "0‌0:0‌0", "0‌0:0‌0", "0‌0:0‌0",
    "♥0♥0♥:♥0♥0♥", "≋0≋0≋:≋0≋0≋",
    "░0░0░:░0░0░", "⊶0⊶0⊶:⊶0⊶0⊶", "⊰0⊱0⊰:⊱0⊱0⊱",
    "⦅0⦆0⦅:⦆0⦆0⦆", "⦑0⦒0⦑:⦒0⦒0⦒", "⧼0⧽0⧼:⧽0⧽0⧽",
    "⨀0⨀0⨀:⨀0⨀0⨀", "⨌0⨌0⨌:⨌0⨌0⨌", "⩴0⩴0⩴:⩴0⩴0⩴",
    "⪉0⪉0⪉:⪉0⪉0⪉", "⫶0⫶0⫶:⫶0⫶0⫶",
    "⬘0⬘0⬘:⬘0⬘0⬘", "⬚0⬚0⬚:⬚0⬚0⬚", "⬦0⬦0⬦:⬦0⬦0⬦",
    "⬧0⬧0⬧:⬧0⬧0⬧", "⬨0⬨0⬨:⬨0⬨0⬨",
    "╚0╝0╚:╝0╚0╝", "╠0╣0╠:╣0╠0╣",
    "『0』『0』『:』『0』『0』", "【0】【0】【:】【0】【0】",
    "〖0〗0〖:〗0〖0〗", "〘0〙0〘:〙0〙0〙", "〚0〛0〚:〛0〛0〛",
    "〝0〞0〝:〞0〞0〞", "〟0〟0〟:〟0〟0〟",
    "﹅0﹆0﹅:﹆0﹆0﹆", "﹉0﹊0﹉:﹊0﹊0﹊",
    "﹋0﹌0﹋:﹌0﹌0﹌", "﹎0﹏0﹎:﹏0﹏0﹏",
    "﹐0﹑0﹐:﹑0﹑0﹑", "﹔0﹕0﹔:﹕0﹕0﹕",
    "﹖0﹗0﹖:﹗0﹗0﹗", "﹙0﹚0﹙:﹚0﹚0﹚",
]

def stylize_time(hh, mm, font_index):
    template = FONTS[font_index - 1] if 1 <= font_index <= len(FONTS) else FONTS[0]
    return template.replace("0", "{}").format(hh[0], hh[1], mm[0], mm[1])

def register_clock(client, state, save_state):

    async def update_last_name():
        while True:
            if state.get("clock_on", False):
                now = datetime.now(IRAN_TZ).strftime("%H%M")  # ساعت ایران
                hh, mm = now[:2], now[2:]
                idx = state.get("clock_font", 1)
                clock_text = stylize_time(hh, mm, idx)
                try:
                    await client(functions.account.UpdateProfileRequest(
                        last_name=f"🕰 {clock_text}"
                    ))
                except Exception as e:
                    print("⚠️ خطا در آپدیت فامیل:", e)
            await asyncio.sleep(60)

    @client.on(events.NewMessage(pattern=r"\.ساعت$"))
    async def toggle_clock(event):
        if event.sender_id != state["owner_id"]: return
        state["clock_on"] = not state.get("clock_on", False)
        save_state()
        await event.edit("🕰 ساعت " + ("✅ روشن شد" if state["clock_on"] else "❌ خاموش شد"))

    @client.on(events.NewMessage(pattern=r"\.ساعت (\d+)$"))
    async def set_font(event):
        if event.sender_id != state["owner_id"]: return
        idx = int(event.pattern_match.group(1))
        if not 1 <= idx <= len(FONTS):
            return await event.edit("❌ شماره فونت باید بین 1 تا 52 باشه")
        state["clock_font"] = idx
        save_state()
        await event.edit(f"🔤 فونت ساعت روی {idx} تنظیم شد")

    client.loop.create_task(update_last_name())
