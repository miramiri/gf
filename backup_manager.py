import os
from telethon import events

def register_backup_manager(client, state):
    @client.on(events.NewMessage(pattern=r"\.بکاپ$"))
    async def backup_all(event):
        # فقط مالک بتونه بگیره
        if event.sender_id != state.get("owner_id"):
            return

        sent_any = False
        for file in os.listdir("."):
            if file.startswith("data_acc") and file.endswith(".json"):
                try:
                    await client.send_file("me", file, caption=f"📦 بکاپ فایل: {file}")
                    sent_any = True
                except Exception as e:
                    await client.send_message("me", f"⚠️ خطا در ارسال {file}: {e}")

        if not sent_any:
            await client.send_message("me", "❌ هیچ فایل دیتایی پیدا نشد.")
        else:
            await client.send_message("me", "✅ همه فایل‌های دیتا فرستاده شد.")