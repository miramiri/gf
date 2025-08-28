import asyncio
import datetime
import pytz
from telethon import events
from telethon.tl.functions.account import UpdateProfileRequest

# وضعیت ساعت
clock_enabled = False
selected_font = 1  # فونت پیش‌فرض

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
    "﹙0﹚0﹙:﹚0﹚0﹚"
]

# گرفتن ساعت ایران
def get_iran_time():
    tz = pytz.timezone("Asia/Tehran")
    return datetime.datetime.now(tz).strftime("%H:%M")


# فرمان انتخاب فونت
@client.on(events.NewMessage(pattern=r'^\.ساعت (\d+)$'))
async def set_font(event):
    global selected_font
    num = int(event.pattern_match.group(1))
    if 1 <= num <= len(FONTS):
        selected_font = num
        await event.reply(f"✅ فونت شماره {num} انتخاب شد")
    else:
        await event.reply("❌ شماره فونت نامعتبره")


# فرمان روشن
@client.on(events.NewMessage(pattern=r'^\.ساعت روشن$'))
async def enable_clock(event):
    global clock_enabled
    clock_enabled = True
    await event.reply("⏰ ساعت پروفایل روشن شد")


# فرمان خاموش
@client.on(events.NewMessage(pattern=r'^\.ساعت خاموش$'))
async def disable_clock(event):
    global clock_enabled
    clock_enabled = False
    try:
        await client(UpdateProfileRequest(last_name=""))
    except:
        pass
    await event.reply("🛑 ساعت پروفایل خاموش شد")


# فرمان لیست ساعت
@client.on(events.NewMessage(pattern=r'^\.لیست ساعت$'))
async def list_fonts(event):
    msg = "📜 لیست فونت‌های ساعت:\n\n"
    for i, f in enumerate(FONTS, start=1):
        msg += f"{i} ➤ {f}\n"
    msg += "\n📌 راهنما:\n"
    msg += "➤ `.ساعت n` : انتخاب فونت شماره n\n"
    msg += "➤ `.ساعت روشن` : روشن کردن ساعت\n"
    msg += "➤ `.ساعت خاموش` : خاموش کردن ساعت\n"
    await event.respond(msg)


# حلقه آپدیت
async def update_clock():
    global clock_enabled, selected_font
    while True:
        if clock_enabled:
            now = get_iran_time()
            style = FONTS[selected_font - 1]
            h, m = now.split(":")

            # جایگذاری عددها
            styled = style
            for c in h + ":" + m:
                styled = styled.replace("0", c, 1)

            try:
                await client(UpdateProfileRequest(last_name=styled))
            except Exception as e:
                print("خطا در آپدیت:", e)

            await asyncio.sleep(60)  # هر دقیقه
        else:
            await asyncio.sleep(5)


# اجرا
with client:
    client.loop.create_task(update_clock())
    client.run_until_disconnected()