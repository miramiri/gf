import asyncio
from datetime import datetime
from telethon import events
from telethon.tl.functions.account import UpdateProfileRequest

# --------- منطقه‌زمانی (Tehran پیش‌فرض) ----------
try:
    from zoneinfo import ZoneInfo  # Python 3.9+
except Exception:
    ZoneInfo = None  # اگر نبود، از UTC استفاده می‌کنیم

# --------- مپ ارقام برای فونت‌های عددی (۱..۱۳) ----------
ALT_DIGITS = {
    1:  "𝟶𝟷𝟸𝟹𝟺𝟻𝟼𝟽𝟾𝟿",
    2:  "𝟘𝟙𝟚𝟛𝟜𝟝𝟞𝟟𝟠𝟡",
    3:  "⓪①②③④⑤⑥⑦⑧⑨",
    4:  "⓪①②③④⑤⑥⑦⑧⑨",
    5:  "⓿❶❷❸❹❺❻❼❽❾",
    6:  "𝟢𝟣𝟤𝟥𝟦𝟧𝟨𝟩𝟪𝟫",
    7:  "𝟬𝟭𝟮𝟯𝟰𝟱𝟲𝟳𝟴𝟵",
    8:  "𝟎𝟏𝟐𝟑𝟒𝟓𝟔𝟕𝟖𝟗",
    9:  "０１２３４５６７８９",
    10: "₀₁₂₃₄₅₆₇₈₉",
    11: "⁰¹²³⁴⁵⁶⁷⁸⁹",
    12: "⓪①②③④⑤⑥⑦⑧⑨",
    13: "𝟶𝟷𝟸𝟹𝟺𝟻𝟼𝟽𝟾𝟿",
}

# --------- قالب‌های ۵۲تایی (برای ۱..۱۳ «00:00»، بقیه دکوری) ----------
TEMPLATES = {
    1:  "00:00",
    2:  "00:00",
    3:  "00:00",
    4:  "00:00",
    5:  "00:00",
    6:  "00:00",
    7:  "00:00",
    8:  "00:00",
    9:  "00:00",
    10: "00:00",
    11: "00:00",
    12: "00:00",
    13: "00:00",
    14: "0҉0҉:0҉0҉",
    15: "0‌0:0‌0",
    16: "0​0:0​0",
    17: "0‍0:0‍0",
    18: "♥0♥0♥:♥0♥0♥",
    19: "≋0≋0≋:≋0≋0≋",
    20: "░0░0░:░0░0░",
    21: "⊶0⊶0⊶:⊶0⊶0⊶",
    22: "⊰0⊱0⊰:⊱0⊱0⊱",
    23: "⦅0⦆0⦅:⦆0⦆0⦆",
    24: "⦑0⦒0⦑:⦒0⦒0⦒",
    25: "⧼0⧽0⧼:⧽0⧽0⧽",
    26: "⨀0⨀0⨀:⨀0⨀0⨀",
    27: "⨌0⨌0⨌:⨌0⨌0⨌",
    28: "⩴0⩴0⩴:⩴0⩴0⩴",
    29: "⪉0⪉0⪉:⪉0⪉0⪉",
    30: "⫶0⫶0⫶:⫶0⫶0⫶",
    31: "⬘0⬘0⬘:⬘0⬘0⬘",
    32: "⬚0⬚0⬚:⬚0⬚0⬚",
    33: "⬦0⬦0⬦:⬦0⬦0⬦",
    34: "⬧0⬧0⬧:⬧0⬧0⬧",
    35: "⬨0⬨0⬨:⬨0⬨0⬨",
    36: "╚0╝0╚:╝0╚0╝",
    37: "╠0╣0╠:╣0╠0╣",
    38: "『0』『0』『:』『0』『0』",
    39: "【0】【0】【:】【0】【0】",
    40: "〖0〗0〖:〗0〖0〗",
    41: "〘0〙0〘:〙0〙0〙",
    42: "〚0〛0〚:〛0〛0〛",
    43: "〝0〞0〝:〞0〞0〞",
    44: "〟0〟0〟:〟0〟0〟",
    45: "﹅0﹆0﹅:﹆0﹆0﹆",
    46: "﹉0﹊0﹉:﹊0﹊0﹊",
    47: "﹋0﹌0﹋:﹌0﹌0﹌",
    48: "﹎0﹏0﹎:﹏0﹏0﹏",
    49: "﹐0﹑0﹐:﹑0﹑0﹑",
    50: "﹔0﹕0﹔:﹕0﹕0﹕",
    51: "﹖0﹗0﹖:﹗0﹗0﹗",
    52: "﹙0﹚0﹙:﹚0﹚0﹚",
}

# ---- تبدیل چهار رقم "HHMM" به فونت و ریختن در قالب ----
def render_time(time_str: str, font_id: int) -> str:
    # time_str مثل "03:50"
    hhmm = time_str.replace(":", "")  # "0350"
    # 1) ارقام را (اگر لازم بود) به فونت عددی تبدیل کن
    digits_map = ALT_DIGITS.get(font_id)
    if digits_map:
        trans = str.maketrans("0123456789", digits_map[:10])
        queue = list(hhmm.translate(trans))  # ['𝟶','𝟹','𝟻','𝟶'] مثلا
    else:
        queue = list(hhmm)  # ['0','3','5','0'] برای فونت‌های دکوری

    # 2) قالب را بگیر و به ترتیب هر '0' را با یک رقم جایگزین کن
    template = TEMPLATES.get(font_id, "00:00")
    out = []
    for ch in template:
        if ch == "0":
            out.append(queue.pop(0) if queue else "0")
        else:
            out.append(ch)
    return "".join(out)

def _now_text(tz_name: str) -> str:
    if ZoneInfo:
        try:
            return datetime.now(ZoneInfo(tz_name)).strftime("%H:%M")
        except Exception:
            pass
    # fallback: UTC
    return datetime.utcnow().strftime("%H:%M")

def register_clock(client, state, save_state):

    async def updater():
        while True:
            try:
                if state.get("clock_on", False):
                    tz = state.get("clock_tz", "Asia/Tehran")
                    now_txt = _now_text(tz)
                    font_id = int(state.get("clock_font", 1))
                    formatted = render_time(now_txt, font_id)

                    # فقط last_name رو آپدیت کن تا first_name/بیو دست‌نخورده بمونه
                    await client(UpdateProfileRequest(last_name=formatted))
                    print(f"⏰ {tz} -> {now_txt} | set: {formatted}")
                # خواب تا مرز دقیقه بعدی (برای دقت)
                tz = state.get("clock_tz", "Asia/Tehran")
                if ZoneInfo:
                    sec = datetime.now(ZoneInfo(tz)).second
                else:
                    sec = datetime.utcnow().second
                await asyncio.sleep(60 - sec if sec < 60 else 60)
            except Exception as e:
                print("⚠️ clock error:", e)
                await asyncio.sleep(15)

    client.loop.create_task(updater())

    # روشن/خاموش
    @client.on(events.NewMessage(pattern=r"\.ساعت (روشن|خاموش)$"))
    async def toggle_clock(event):
        if event.sender_id != state["owner_id"]:
            return
        on = (event.pattern_match.group(1) == "روشن")
        state["clock_on"] = on
        save_state()
        await event.edit(f"⏰ ساعت {'روشن' if on else 'خاموش'} شد.")

    # انتخاب فونت
    @client.on(events.NewMessage(pattern=r"\.ساعت فونت (\d+)$"))
    async def set_font(event):
        if event.sender_id != state["owner_id"]:
            return
        n = int(event.pattern_match.group(1))
        if 1 <= n <= 52:
            state["clock_font"] = n
            save_state()
            sample = render_time("00:00", n)
            await event.edit(f"🔤 فونت {n} ست شد → {sample}")
        else:
            await event.edit("❌ شماره فونت باید بین ۱ تا ۵۲ باشه.")

    # تنظیم منطقه زمانی
    @client.on(events.NewMessage(pattern=r"\.ساعت منطقه (.+)$"))
    async def set_tz(event):
        if event.sender_id != state["owner_id"]:
            return
        tz = event.pattern_match.group(1).strip()
        # تست سریع
        try:
            test = _now_text(tz)
        except Exception:
            test = None
        if test:
            state["clock_tz"] = tz
            save_state()
            await event.edit(f"🌍 منطقه‌زمانی روی **{tz}** ست شد. الان: {test}")
        else:
            await event.edit("❌ نام منطقه‌زمانی نادرست است. مثل: `Asia/Tehran` یا `Europe/Berlin`")

    # وضعیت/منو
    @client.on(events.NewMessage(pattern=r"\.لیست ساعت$"))
    async def clock_list(event):
        if event.sender_id != state["owner_id"]:
            return
        tz = state.get("clock_tz", "Asia/Tehran")
        now_txt = _now_text(tz)
        header = f"""ıllıllııllıllııllıllııllıllııllıllııllıllııllıllııllıllııllı
🕰️ ساعت 
══════●═══════════════
✧ .ساعت ⤳ (روشن یا خاموش)

🔄 وضعیت ساعت
——————————