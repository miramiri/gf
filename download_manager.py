
import os
import asyncio
from telethon import events

DOWNLOAD_DIR = "downloads"

def register_download_manager(client, state, save_state):
    if "download_queue" not in state:
        state["download_queue"] = []

    if not os.path.exists(DOWNLOAD_DIR):
        os.makedirs(DOWNLOAD_DIR)

    async def watchdog():
        while True:
            if state["download_queue"]:
                msg_id = state["download_queue"][0]
                try:
                    msg = await client.get_messages("me", ids=msg_id)
                    if msg and msg.media:
                        filename = os.path.join(DOWNLOAD_DIR, f"{msg.id}")
                        # تلاش تا دانلود کامل بشه
                        while True:
                            try:
                                path = await msg.download_media(file=filename)
                                if path and os.path.exists(path):
                                    print(f"✅ دانلود کامل شد: {path}")
                                    # فرستادن فایل به سیو مسیج
                                    await client.send_message(
                                        "me",
                                        f"✅ فایل دانلود شد:\n`{os.path.basename(path)}`",
                                        file=path
                                    )
                                    break
                            except Exception as e:
                                print("⚠️ دانلود قطع شد، تلاش مجدد...", e)
                                await asyncio.sleep(5)  # کمی صبر و دوباره تلاش
                        # پاک کردن از صف
                        state["download_queue"].pop(0)
                        save_state()
                    else:
                        # اگه فایل دیگه وجود نداشت
                        state["download_queue"].pop(0)
                        save_state()
                except Exception as e:
                    print("⚠️ خطا در پردازش دانلود:", e)
            await asyncio.sleep(3)

    client.loop.create_task(watchdog())

    @client.on(events.NewMessage(pattern=r"\.دانلود$"))
    async def add_to_queue(event):
        if event.sender_id != state["owner_id"]:
            return
        if not event.is_reply:
            await event.reply("❌ روی فایل ریپلای کن.")
            return
        reply = await event.get_reply_message()
        if not reply.media:
            await event.reply("❌ این پیام فایل نداره.")
            return
        if reply.id not in state["download_queue"]:
            state["download_queue"].append(reply.id)
            save_state()
            await event.reply("📥 فایل به صف دانلود اضافه شد.")
        else:
            await event.reply("ℹ️ این فایل قبلاً توی صف بود.")
