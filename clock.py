
import asyncio
import datetime
import pytz
from telethon import events
from telethon.tl.functions.account import UpdateProfileRequest

# وضعیت ساعت
clock_enabled = False
selected_font = 1  # فونت پیش‌فرض

# صفرهای قابل‌جایگزینی در استایل‌ها (برای پشتیبانی از انواع یونیکدی صفر)
ZERO_CHARS = set("0𝟘𝟎𝟬０⓪⓿⁰₀")

FONTS = [
    "00:00",
    "𝟘𝟘:𝟘𝟘",
    "⓪⓪:⓪⓪",
    "⓿⓿:⓿⓿",
    "𝟢𝟢:𝟢𝟢",
    "𝟬𝟬:𝟬𝟬",
    "𝟎𝟎:𝟎𝟎",
    "００:００",
    "₀₀:₀₀",
    "⁰⁰:⁰⁰",
    "҉0҉0҉:҉0҉0҉",
    "⟦0⟧⟦0⟧:⟦0⟧⟦0⟧",
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
    "﹙0﹚0﹙:﹚0﹚0﹚"
]

def get_iran_time():
    tz = pytz.timezone("Asia/Tehran")
    return datetime.datetime.now(tz).strftime("%H:%M")

def _replace_next_zero(s: str, ch: str) -> tuple[str, bool]:
    for i, c in enumerate(s):
        if c in ZERO_CHARS:
            return s[:i] + ch + s[i+1:], True
    return s, False

def register_clock(client, state=None, save_state=None):
    @client.on(events.NewMessage(pattern=r'^\.ساعت (\d+)$'))
    async def set_font(event):
        global selected_font
        num = int(event.pattern_match.group(1))
        if 1 <= num <= len(FONTS):
            selected_font = num
            await event.edit(f"✅ فونت شماره {num} انتخاب شد")
        else:
            await event.edit("❌ شماره فونت نامعتبره")

    @client.on(events.NewMessage(pattern=r'^\.ساعت روشن$'))
    async def enable_clock(event):
        global clock_enabled
        clock_enabled = True
        await event.edit("⏰ ساعت پروفایل روشن شد")

    @client.on(events.NewMessage(pattern=r'^\.ساعت خاموش$'))
    async def disable_clock(event):
        global clock_enabled
        clock_enabled = False
        try:
            await client(UpdateProfileRequest(last_name=""))
        except Exception:
            pass
        await event.edit("🛑 ساعت پروفایل خاموش شد")

    @client.on(events.NewMessage(pattern=r'^\.لیست ساعت$'))
    async def list_fonts(event):
        msg = "📜 لیست فونت‌های ساعت:\n\n"
        for i, f in enumerate(FONTS, start=1):
            msg += f"{i} ➤ {f}\n"
        msg += "\n📌 راهنما:\n"
        msg += "➤ `.ساعت n` : انتخاب فونت شماره n\n"
        msg += "➤ `.ساعت روشن` : روشن کردن ساعت\n"
        msg += "➤ `.ساعت خاموش` : خاموش کردن ساعت\n"
        await event.edit(msg)

    async def update_clock():
        global clock_enabled, selected_font
        while True:
            if clock_enabled:
                now = get_iran_time()
                h, m = now.split(":")
                digits = h + m
                style = FONTS[selected_font - 1]
                styled = style

                for d in digits:
                    styled, replaced = _replace_next_zero(styled, d)
                    if not replaced:
                        break

                try:
                    await client(UpdateProfileRequest(last_name=styled))
                except Exception as e:
                    print("خطا در آپدیت:", e)
                await asyncio.sleep(60)
            else:
                await asyncio.sleep(5)

    client.loop.create_task(update_clock())
