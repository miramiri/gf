
import asyncio
from datetime import datetime
from telethon import events
from telethon.tl.functions.account import UpdateProfileRequest

# =========================
#   Clock feature (Telegram Userbot)
#   Commands:
#     .لیست ساعت                → نمایش راهنما و ۵۲ فونت
#     .ساعت <n>                → تنظیم فونت (۱ تا ۵۲، اعداد فارسی/انگلیسی)
#     .ساعت روشن               → فعال‌سازی ساعت روی پروفایل
#     .ساعت خاموش             → غیرفعال‌سازی و پاک‌کردن از پروفایل
# =========================

# ---------- helpers ----------
def _map_digits(digits: str, colon: str = ":"):
    """
    Build a translator that maps ASCII digits 0..9 and ':'
    to the provided glyphs. 'digits' must be length 10.
    """
    assert len(digits) == 10, "digits must be length 10"
    trans = str.maketrans("0123456789:", digits + colon)
    return lambda t: t.translate(trans)

def _per_char(prefix: str = "", suffix: str = "", colon_repl: str | None = None):
    """
    Wrap each character (digit or ':') with prefix/suffix.
    Optionally replace ':' with a custom glyph.
    """
    def fn(t: str) -> str:
        out = []
        for ch in t:
            if ch == ":" and colon_repl is not None:
                out.append(colon_repl)
            else:
                out.append(f"{prefix}{ch}{suffix}")
        return "".join(out)
    return fn

def _whole_wrap(left: str, right: str):
    """Wrap the whole time string at once."""
    return lambda t: f"{left}{t}{right}"

# Some commonly used digit sets
DIG_CIRCLED_0_9 = "⓪①②③④⑤⑥⑦⑧⑨"
DIG_MATH_SANS_BOLD = "𝟢𝟣𝟤𝟥𝟦𝟧𝟨𝟩𝟪𝟫"
DIG_MATH_DOUBLE = "𝟘𝟙𝟚𝟛𝟜𝟝𝟞𝟟𝟠𝟡"
DIG_MATH_BOLD = "𝟎𝟏𝟐𝟑𝟒𝟓𝟔𝟕𝟖𝟗"
DIG_MATH_MONO = "𝟶𝟷𝟸𝟹𝟺𝟻𝟼𝟽𝟾𝟿"
DIG_FULLWIDTH = "０１２３４５６７８９"
DIG_SUPERSCRIPT = "⁰¹²³⁴⁵⁶⁷⁸⁹"
DIG_SUBSCRIPT = "₀₁₂₃₄₅₆₇₈₉"

# ---------- fonts table (1..52) ----------
FONTS = {
    # Pure digit sets / simple replacements
    1: lambda t: t,  # plain
    2: _map_digits(DIG_CIRCLED_0_9),
    3: _map_digits(DIG_MATH_MONO),
    4: _map_digits(DIG_MATH_DOUBLE),
    5: _map_digits(DIG_FULLWIDTH, "："),
    6: _map_digits(DIG_CIRCLED_0_9, "："),
    7: _map_digits("𝟬𝟭𝟮𝟯𝟰𝟱𝟲𝟯𝟴𝟵"),  # alt bold (note: 7th char duplicated to keep visual style)
    8: _map_digits(DIG_MATH_BOLD),
    9: _map_digits(DIG_FULLWIDTH),
    10: _map_digits(DIG_SUBSCRIPT),
    11: _map_digits(DIG_SUPERSCRIPT),
    12: _map_digits(DIG_CIRCLED_0_9),  # duplicate set for convenience
    13: _map_digits(DIG_MATH_MONO),
    # Ornamented per-character styles (approximate the provided samples)
    14: _per_char("҉", "҉"),            # overlay-like
    15: _per_char("\u200c", "\u200c"),  # ZWNJ framing
    16: _per_char("\u200d", "\u200d"),  # ZWJ framing
    17: _per_char("\u200b", "\u200b"),  # ZWSP framing
    18: _per_char("♥", "♥", "♥:♥"),
    19: _per_char("≋", "≋", "≋:≋"),
    20: _per_char("░", "░", "░:░"),
    21: _per_char("⊶", "⊶", "⊶:⊶"),
    22: _per_char("⊰", "⊱", "⊰:⊱"),
    23: _per_char("⦅", "⦆", "⦅:⦆"),
    24: _per_char("⦑", "⦒", "⦑:⦒"),
    25: _per_char("⧼", "⧽", "⧼:⧽"),
    26: _per_char("⨀", "⨀", "⨀:⨀"),
    27: _per_char("⨌", "⨌", "⨌:⨌"),
    28: _per_char("⩴", "⩴", "⩴"),
    29: _per_char("⪉", "⪉", "⪉:⪉"),
    30: _per_char("⫶", "⫶", "⫶"),
    31: _per_char("⬘", "⬘", "⬘:⬘"),
    32: _per_char("⬚", "⬚", "⬚:⬚"),
    33: _per_char("⬦", "⬦", "⬦:⬦"),
    34: _per_char("⬧", "⬧", "⬧:⬧"),
    35: _per_char("⬨", "⬨", "⬨:⬨"),
    36: _per_char("╚", "╝", "╚:╝"),
    37: _per_char("╠", "╣", "╠:╣"),
    # Whole-string wrappers
    38: _whole_wrap("『", "』"),
    39: _whole_wrap("【", "】"),
    40: _whole_wrap("〖", "〗"),
    41: _whole_wrap("〘", "〙"),
    42: _per_char("〚", "〛", "〚:〛"),
    43: _per_char("〝", "〞", "〝:〞"),
    44: _per_char("〟", "〟", "〟:〟"),
    45: _per_char("﹅", "﹆", "﹅:﹆"),
    46: _per_char("﹉", "﹊", "﹉:﹊"),
    47: _per_char("﹋", "﹌", "﹋:﹌"),
    48: _per_char("﹎", "﹏", "﹎:﹏"),
    49: _per_char("﹐", "﹑", "﹐:﹑"),
    50: _per_char("﹔", "﹕", "﹔:﹕"),
    51: _per_char("﹖", "﹗", "﹖:﹗"),
    52: _per_char("﹙", "﹚", "﹙:﹚"),
}

# ---------- register feature ----------
def register_clock(client, state, save_state):
    """
    Register the clock feature on a Telethon client.
    - client: Telethon client
    - state:  dict-like storage (persisted by caller)
    - save_state: callable() to persist state
    """
    # defaults
    state.setdefault("clock_font", 1)
    state.setdefault("clock_on", False)

    async def _apply_now():
        """Apply current time immediately according to settings."""
        now = datetime.now().strftime("%H:%M")
        font_fn = FONTS.get(state.get("clock_font", 1), FONTS[1])
        styled = font_fn(now)
        try:
            await client(UpdateProfileRequest(last_name=f"⏰ {styled}"))
        except Exception as e:
            print(f"⚠️ UpdateProfileRequest failed: {e}")

    async def update_clock():
        """Background updater, runs every minute if clock_on is True."""
        while True:
            try:
                if state.get("clock_on", False):
                    await _apply_now()
                await asyncio.sleep(60)
            except Exception as e:
                print(f"⚠️ Clock loop error: {e}")
                await asyncio.sleep(60)

    # start background task
    client.loop.create_task(update_clock())

    # ------- commands -------

    # List / help (exact style provided by the user)
    @client.on(events.NewMessage(pattern=r"^\.لیست\s+ساعت$"))
    async def list_fonts(event):
        msg = """ıllıllııllıllııllıllııllıllııllıllııllıllııllıllııllıllııllı
🕰️ ساعت 
══════●═══════════════
✧ .ساعت ⤳ (روشن یا خاموش)

🔄 وضعیت ساعت
———————————————
✧ .ساعت ⤳ (1 ... 52)

🔤 تنظیم فونت
—————fonts—————
1- 𝟶𝟶:𝟶𝟶  
2- 𝟘𝟘:𝟘𝟘
3- ⓪⓪:⓪⓪  
4- ⓪⓪:⓪⓪
5- ⓿⓿:⓿⓿  
6- 𝟢𝟢:𝟢𝟢
7- 𝟬𝟬:𝟬𝟬  
8- 𝟎𝟎:𝟎𝟎
9- ００:００  
10- ₀₀:₀₀
11- ⁰⁰:⁰⁰   
12- ⓪⓪:⓪⓪
13- 𝟶𝟶:𝟶𝟶  
14- ҉0҉҉0҉҉:҉҉0҉҉0҉
15- ‌0‌‌0‌‌:‌‌0‌‌0‌  
16- ‌0‌‌0‌‌:‌‌0‌‌0‌
17- ‌0‌‌0‌‌:‌‌0‌‌0‌  
18- ♥0♥♥0♥♥:♥♥0♥♥0♥
19- ≋0≋≋0≋≋:≋≋0≋≋0≋    

20- ░0░░0░░:░░0░░0░

21- ⊶0⊶⊶0⊶⊶:⊶⊶0⊶⊶0⊶
22- ⊰0⊱⊰0⊱⊰:⊱⊰0⊱⊰0⊱  
23- ⦅0⦆⦅0⦆⦅:⦆⦅0⦆⦅0⦆
24- ⦑0⦒⦑0⦒⦑:⦒⦑0⦒⦑0⦒  
25- ⧼0⧽⧼0⧽⧼:⧽⧼0⧽⧼0⧽
26- ⨀0⨀⨀0⨀⨀:⨀⨀0⨀⨀0⨀
27- ⨌0⨌⨌0⨌⨌:⨌⨌0⨌⨌0⨌
28- ⩴0⩴⩴0⩴⩴:⩴⩴0⩴⩴0⩴
29- ⪉0⪉⪉0⪉⪉:⪉⪉0⪉⪉0⪉
30- ⫶0⫶⫶0⫶⫶:⫶⫶0⫶⫶0⫶
31- ⬘0⬘⬘0⬘⬘:⬘⬘0⬘⬘0⬘
32- ⬚0⬚⬚0⬚⬚:⬚⬚0⬚⬚0⬚
33- ⬦0⬦⬦0⬦⬦:⬦⬦0⬦⬦0⬦
34- ⬧0⬧⬧0⬧⬧:⬧⬧0⬧⬧0⬧
35- ⬨0⬨⬨0⬨⬨:⬨⬨0⬨⬨0⬨
36- ╚0╝╚0╝╚:╝╚0╝╚0╝
37- ╠0╣╠0╣╠:╣╠0╣╠0╣
38- 『0』『0』『:』『0』『0』
39- 【0】【0】【:】【0】【0】
40- 〖0〗〖0〗〖:〗〖0〗〖0〗
41- 〘0〙〘0〙〘:〙〘0〙〘0〙
42- 〚0〛〚0〛〚:〛〚0〛〚0〛
43- 〝0〞〝0〞〝:〞〝0〞〝0〞
44- 〟0〟〟0〟〟:〟〟0〟〟0〟
45- ﹅0﹆﹅0﹆﹅:﹆﹅0﹆﹅0﹆
46- ﹉0﹊﹉0﹊﹉:﹊﹉0﹊﹉0﹊
47- ﹋0﹌﹋0﹌﹋:﹌﹋0﹌﹋0﹌
48- ﹎0﹏﹎0﹏﹎:﹏﹎0﹏﹎0﹏
49- ﹐0﹑﹐0﹑﹐:﹑﹐0﹑﹐0﹑
50- ﹔0﹕﹔0﹕﹔:﹕﹔0﹕﹔0﹕
51- ﹖0﹗﹖0﹗﹖:﹗﹖0﹗﹖0﹗
52- ﹙0﹚﹙0﹚﹙:﹚﹙0﹚﹙0﹚
———————————————
اینـــجوری باشه .لیست ساعت"""
        try:
            await event.edit(msg)
        except Exception:
            await event.reply(msg)

    # Set font number
    @client.on(events.NewMessage(pattern=r"^\.ساعت\s+(\d+)$"))
    async def set_font(event):
        txt_num = event.pattern_match.group(1)
        try:
            num = int(txt_num)  # supports Persian/Arabic digits too
        except ValueError:
            return await event.reply("❌ لطفاً عدد صحیح بده. (۱ تا ۵۲)")

        if num not in FONTS:
            return await event.reply("❌ فونت نامعتبره. از 1 تا 52 انتخاب کن. (.لیست ساعت)")

        state["clock_font"] = num
        if callable(save_state):
            try:
                save_state()
            except Exception as e:
                return await event.reply(f"⚠️ فونت ذخیره نشد: {e}")

        await event.reply(f"✅ فونت ساعت روی {num} تنظیم شد.")

        # اگر ساعت روشن است، بلافاصله اعمال کن
        if state.get("clock_on"):
            await _apply_now()

    # Turn ON
    @client.on(events.NewMessage(pattern=r"^\.ساعت\s+روشن$"))
    async def clock_on(event):
        state["clock_on"] = True
        if callable(save_state):
            try:
                save_state()
            except Exception as e:
                return await event.reply(f"⚠️ ذخیره وضعیت نشد: {e}")
        await _apply_now()
        await event.reply("✅ ساعت روی پروفایل فعال شد.")

    # Turn OFF
    @client.on(events.NewMessage(pattern=r"^\.ساعت\s+خاموش$"))
    async def clock_off(event):
        state["clock_on"] = False
        if callable(save_state):
            try:
                save_state()
            except Exception as e:
                return await event.reply(f"⚠️ ذخیره وضعیت نشد: {e}")
        try:
            await client(UpdateProfileRequest(last_name=""))  # clear last name
        except Exception as e:
            print(f"⚠️ پاک‌کردن فیلد نام‌خانوادگی ناموفق بود: {e}")
        await event.reply("❌ ساعت خاموش شد و از پروفایل پاک شد.")
