import asyncio
from datetime import datetime
import pytz
from telethon import events, functions

IRAN_TZ = pytz.timezone("Asia/Tehran")

# وضعیت ساعت و فونت (در حافظه)
clock_on = False
clock_font = 1

# فونت‌ها مثل قبل
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

def register_clock(client):

    async def update_last_name():
        global clock_on, clock_font
        while True:
            if clock_on:
                now = datetime.now(IRAN_TZ).strftime("%H%M")
                hh, mm = now[:2], now[2:]
                clock_text = stylize_time(hh, mm, clock_font)
                try:
                    await client(functions.account.UpdateProfileRequest(
                        last_name=f" {clock_text}"
                    ))
                except Exception as e:
                    print("⚠️ خطا در آپدیت فامیل:", e)
            await asyncio.sleep(60)

    @client.on(events.NewMessage(pattern=r"\.ساعت$"))
    async def toggle_clock(event):
        global clock_on
        clock_on = not clock_on
        await event.edit("🕰 ساعت " + ("✅ روشن شد" if clock_on else "❌ خاموش شد"))

    @client.on(events.NewMessage(pattern=r"\.ساعت (\d+)$"))
    async def set_font(event):
        global clock_font
        idx = int(event.pattern_match.group(1))
        if not 1 <= idx <= len(FONTS):
            return await event.edit("❌ شماره فونت باید بین 1 تا 52 باشه")
        clock_font = idx
        await event.edit(f"🔤 فونت ساعت روی {idx} تنظیم شد")

    @client.on(events.NewMessage(pattern=r"\.لیست ساعت$"))
    async def list_clock_fonts(event):
        text = (
            "ıllıllııllıllııllıllııllıllııllıllııllıllııllıllııllıllııllı\n"
            "🕰️ ساعت \n"
            "══════●═══════════════\n"
            "✧ .ساعت ⤳ (روشن یا خاموش)\n\n"
            "🔄 وضعیت ساعت\n"
            "———————————————\n"
            "✧ .ساعت فونت ⤳ (1 ... 52)\n\n"
            "🔤 تنظیم فونت\n"
            "———————————————\n"
            "—————fonts—————\n"
        )
        for i, f in enumerate(FONTS, start=1):
            sample = f.replace("0","0")  # نمایش نمونه خام
            text += f"{i}- {sample}\n"
        await event.edit(text)

    client.loop.create_task(update_last_name())