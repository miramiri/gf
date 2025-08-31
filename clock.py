import asyncio
from datetime import datetime
from telethon import events
from telethon.tl.functions.account import UpdateProfileRequest

# 🔢 تمام فونت‌ها
DIGITS = {
    1: "𝟶𝟷𝟸𝟹𝟺𝟻𝟼𝟽𝟾𝟿",
    2: "𝟘𝟙𝟚𝟛𝟜𝟝𝟞𝟟𝟠𝟡",
    3: "⓪①②③④⑤⑥⑦⑧⑨",
    4: "⓪①②③④⑤⑥⑦⑧⑨",
    5: "⓿❶❷❸❹❺❻❼❽❾",
    6: "𝟢𝟣𝟤𝟥𝟦𝟧𝟨𝟩𝟪𝟫",
    7: "𝟬𝟭𝟮𝟯𝟰𝟱𝟲𝟳𝟴𝟵",
    8: "𝟎𝟏𝟐𝟑𝟒𝟓𝟔𝟕𝟖𝟗",
    9: "０１２３４５６７８９",
    10: "₀₁₂₃₄₅₆₇₈₉",
    11: "⁰¹²³⁴⁵⁶⁷⁸⁹",
    12: "⓪①②③④⑤⑥⑦⑧⑨",
    13: "𝟶𝟷𝟸𝟹𝟺𝟻𝟼𝟽𝟾𝟿",
    14: "0҉1҉2҉3҉4҉5҉6҉7҉8҉9҉",
    15: "0‌1‌2‌3‌4‌5‌6‌7‌8‌9",
    16: "0​1​2​3​4​5​6​7​8​9",
    17: "0‍1‍2‍3‍4‍5‍6‍7‍8‍9",
    18: "♥0♥1♥2♥3♥4♥5♥6♥7♥8♥9",
    19: "≋0≋1≋2≋3≋4≋5≋6≋7≋8≋9",
    20: "░0░1░2░3░4░5░6░7░8░9",
    21: "⊶0⊶1⊶2⊶3⊶4⊶5⊶6⊶7⊶8⊶9",
    22: "⊰0⊱1⊰2⊱3⊰4⊱5⊰6⊱7⊰8⊱9",
    23: "⦅0⦆1⦅2⦆3⦅4⦆5⦅6⦆7⦅8⦆9",
    24: "⦑0⦒1⦑2⦒3⦑4⦒5⦑6⦒7⦑8⦒9",
    25: "⧼0⧽1⧼2⧽3⧼4⧽5⧼6⧽7⧼8⧽9",
    26: "⨀0⨀1⨀2⨀3⨀4⨀5⨀6⨀7⨀8⨀9",
    27: "⨌0⨌1⨌2⨌3⨌4⨌5⨌6⨌7⨌8⨌9",
    28: "⩴0⩴1⩴2⩴3⩴4⩴5⩴6⩴7⩴8⩴9",
    29: "⪉0⪉1⪉2⪉3⪉4⪉5⪉6⪉7⪉8⪉9",
    30: "⫶0⫶1⫶2⫶3⫶4⫶5⫶6⫶7⫶8⫶9",
    31: "⬘0⬘1⬘2⬘3⬘4⬘5⬘6⬘7⬘8⬘9",
    32: "⬚0⬚1⬚2⬚3⬚4⬚5⬚6⬚7⬚8⬚9",
    33: "⬦0⬦1⬦2⬦3⬦4⬦5⬦6⬦7⬦8⬦9",
    34: "⬧0⬧1⬧2⬧3⬧4⬧5⬧6⬧7⬧8⬧9",
    35: "⬨0⬨1⬨2⬨3⬨4⬨5⬨6⬨7⬨8⬨9",
    36: "╚0╝1╚2╝3╚4╝5╚6╝7╚8╝9",
    37: "╠0╣1╠2╣3╠4╣5╠6╣7╠8╣9",
    38: "『0』『1』『2』『3』『4』『5』『6』『7』『8』『9』",
    39: "【0】【1】【2】【3】【4】【5】【6】【7】【8】【9】",
    40: "〖0〗1〖2〗3〖4〗5〖6〗7〖8〗9",
    41: "〘0〙1〘2〙3〘4〙5〘6〙7〘8〙9",
    42: "〚0〛1〚2〛3〚4〛5〚6〛7〚8〛9",
    43: "〝0〞1〝2〞3〝4〞5〝6〞7〝8〞9",
    44: "〟0〟1〟2〟3〟4〟5〟6〟7〟8〟9",
    45: "﹅0﹆1﹅2﹆3﹅4﹆5﹅6﹆7﹅8﹆9",
    46: "﹉0﹊1﹉2﹊3﹉4﹊5﹉6﹊7﹉8﹊9",
    47: "﹋0﹌1﹋2﹌3﹋4﹌5﹋6﹌7﹋8﹌9",
    48: "﹎0﹏1﹎2﹏3﹎4﹏5﹎6﹏7﹎8﹏9",
    49: "﹐0﹑1﹐2﹑3﹐4﹑5﹐6﹑7﹐8﹑9",
    50: "﹔0﹕1﹔2﹕3﹔4﹕5﹔6﹕7﹔8﹕9",
    51: "﹖0﹗1﹖2﹗3﹖4﹗5﹖6﹗7﹖8﹗9",
    52: "﹙0﹚1﹙2﹚3﹙4﹚5﹙6﹚7﹙8﹚9",
}

# 🛠 تابع تبدیل
def convert_time(time_str, font_id):
    digits = DIGITS.get(font_id, DIGITS[1])
    normal_digits = "0123456789"
    trans_table = str.maketrans(normal_digits, digits[:10])
    return time_str.translate(trans_table)


def register_clock(client, state, save_state):

    async def update_lastname():
        while True:
            if state.get("clock_on", False):
                try:
                    now = datetime.now().strftime("%H:%M")
                    font_id = state.get("clock_font", 1)
                    formatted = convert_time(now, font_id)

                    me = await client.get_me()
                    await client(UpdateProfileRequest(
                        first_name=me.first_name or "",
                        last_name=formatted
                    ))
                    print(f"⏰ ساعت آپدیت شد: {formatted}")
                except Exception as e:
                    print("⚠️ خطا در آپدیت ساعت:", e)
            await asyncio.sleep(60)

    client.loop.create_task(update_lastname())

    # روشن / خاموش
    @client.on(events.NewMessage(pattern=r"\.ساعت (روشن|خاموش)$"))
    async def toggle_clock(event):
        if event.sender_id != state["owner_id"]:
            return
        arg = event.pattern_match.group(1)
        state["clock_on"] = (arg == "روشن")
        save_state()
        await event.edit(f"⏰ ساعت {'فعال' if state['clock_on'] else 'غیرفعال'} شد.")

    # تغییر فونت
    @client.on(events.NewMessage(pattern=r"\.ساعت فونت (\d+)$"))
    async def set_font(event):
        if event.sender_id != state["owner_id"]:
            return
        num = int(event.pattern_match.group(1))
        if num in DIGITS:
            state["clock_font"] = num
            save_state()
            await event.edit(f"🔤 فونت ساعت روی {num} تنظیم شد.")
        else:
            await event.edit("❌ این فونت وجود نداره (۱ تا ۵۲).")

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
""" + "\n".join([f"{i}- {convert_time('00:00', i)}" for i in range(1, 53)])
        await event.edit(msg)
