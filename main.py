from telethon import TelegramClient, events, functions
from telethon.tl.functions.photos import UploadProfilePhotoRequest, DeletePhotosRequest
from telethon.tl.functions.account import UpdateProfileRequest
from telethon.tl.types import InputPhoto
import asyncio
from io import BytesIO

# بيانات الجلسة (تم استخدام الجلسة التي رفعتها مباشرة)
api_id = 23988357  # ضع الـ api_id الخاص بك هنا
api_hash = "25bee10ac433f3dc16a2c0d78bb579de"  # ضع الـ api_hash هنا
session_file = "my_session"  # نفس اسم الملف الذي رفعته بدون .session

client = TelegramClient(session_file, api_id, api_hash)

@client.on(events.NewMessage(pattern=r'^\.انتحال$', func=lambda e: e.is_reply))
async def impersonate_user(event):
    replied = await event.get_reply_message()
    if not replied:
        await event.reply("❌ يجب الرد على رسالة المستخدم الذي تريد انتحاله.")
        return

    try:
        target = await replied.get_sender()
        full = await client(functions.users.GetFullUserRequest(target.id))
        name = target.first_name or ""
        lname = target.last_name or ""
        bio = full.about or ""

        # تغيير الاسم والبايو
        await client(UpdateProfileRequest(
            first_name=name,
            last_name=lname,
            about=bio
        ))

        # تغيير الصورة
        photos = await client.get_profile_photos(target)
        if photos and photos.total > 0:
            file = await client.download_media(photos[0], file=BytesIO())
            file.seek(0)
            await client(UploadProfilePhotoRequest(file))
        else:
            # حذف الصورة إن لم يكن لديه صورة
            await client(DeletePhotosRequest(await client.get_profile_photos('me')))

        await event.reply("✅ تم الانتحال بنجاح.")

    except Exception as e:
        await event.reply(f"❌ خطأ أثناء الانتحال:\n{e}")

print("🚀 يتم تشغيل البوت الآن ...")
client.start()
client.run_until_disconnected()