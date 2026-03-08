import asyncio
import smtplib
from email.mime.text import MIMEText
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

# --- بياناتك الشخصية ---
API_ID = 25880715
API_HASH = "0d1e0a5fe75236df18295a0f8b22b458"
BOT_TOKEN = "8650334560:AAFZUZ9Ilgl4OIx5riTB86Mrzo0i2ytsH5w"
# --------------------

app = Client("Boty_Shalal", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# قاعدة بيانات مؤقتة
db = {}

def main_markup():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📧 ايميل الدعم", callback_data="set_target"),
         InlineKeyboardButton("➕ اضف ايميلك", callback_data="add_sender")],
        [InlineKeyboardButton("📝 الموضوع", callback_data="set_sub"),
         InlineKeyboardButton("📋 الكليشه", callback_data="set_msg")],
        [InlineKeyboardButton("🔢 عدد الرسائل", callback_data="set_count"),
         InlineKeyboardButton("⏱️ الثواني", callback_data="set_del")],
        [InlineKeyboardButton("🚀 بدء الارسال", callback_data="start_burn")],
        [InlineKeyboardButton("👤 المطور: سالم", url="https://t.me/hlhrI")]
    ])

@app.on_message(filters.command("start") & filters.private)
async def start(client, message):
    uid = message.from_user.id
    db[uid] = {"target": None, "senders": [], "sub": "No Subject", "msg": "No Message", "count": 10, "delay": 2, "step": None}
    
    welcome_text = (
        "**مرحباً بك في بوت الشد الخارجي (Boty) 🚀**\n\n"
        "قم بضبط إعداداتك من الأزرار بالأسفل.\n\n"
        "**Dev: @hlhrI**"
    )
    await message.reply_text(welcome_text, reply_markup=main_markup())

@app.on_callback_query()
async def callbacks(client, query: CallbackQuery):
    uid = query.from_user.id
    data = query.data
    
    if data == "set_target":
        db[uid]["step"] = "target"
        await query.message.edit_text("🎯 أرسل إيميل الدعم المستهدف:")
    elif data == "add_sender":
        db[uid]["step"] = "sender"
        await query.message.edit_text("📧 أرسل إيميلك وباسورد التطبيقات (email:password):")
    elif data == "set_sub":
        db[uid]["step"] = "sub"
        await query.message.edit_text("📝 أرسل موضوع الرسالة:")
    elif data == "set_msg":
        db[uid]["step"] = "msg"
        await query.message.edit_text("📋 أرسل الكليشه (محتوى الرسالة):")
    elif data == "set_count":
        db[uid]["step"] = "count"
        await query.message.edit_text("🔢 أرسل عدد الرسائل:")
    elif data == "set_del":
        db[uid]["step"] = "delay"
        await query.message.edit_text("⏱️ أرسل الثواني بين الرسائل:")
    elif data == "start_burn":
        if not db[uid]["senders"] or not db[uid]["target"]:
            await query.answer("⚠️ بيانات ناقصة!", show_alert=True)
        else:
            asyncio.create_task(burn_process(client, query.message, uid))

async def burn_process(client, msg, uid):
    user = db[uid]
    success, failed = 0, 0
    await msg.edit_text("🚀 جاري بدء العملية...")
    
    for i in range(int(user["count"])):
        try:
            sender_info = user["senders"][i % len(user["senders"])]
            email_u, pass_u = sender_info.split(":")
            
            m = MIMEText(user["msg"])
            m["Subject"], m["From"], m["To"] = user["sub"], email_u, user["target"]
            
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login(email_u, pass_u)
                server.sendmail(email_u, user["target"], m.as_string())
            success += 1
        except:
            failed += 1
            
        status = (
            "**🚀 عملية الشد جارية...**\n\n"
            f"✅ ناجح: {success}\n"
            f"❌ فشل: {failed}\n"
            f"🎯 الهدف: `{user['target']}`\n\n"
            f"**بواسطة: @hlhrI**"
        )
        try: await msg.edit_text(status)
        except: pass
        await asyncio.sleep(int(user["delay"]))
    
    await client.send_message(uid, "✅ انتهت العملية بنجاح!")

@app.on_message(filters.text & filters.private)
async def handle_inputs(client, message):
    uid = message.from_user.id
    if uid not in db or not db[uid]["step"]: return
    
    step = db[uid]["step"]
    val = message.text
    
    if step == "target": db[uid]["target"] = val
    elif step == "sender": db[uid]["senders"].append(val)
    elif step == "sub": db[uid]["sub"] = val
    elif step == "msg": db[uid]["msg"] = val
    elif step == "count": db[uid]["count"] = int(val) if val.isdigit() else 10
    elif step == "delay": db[uid]["delay"] = int(val) if val.isdigit() else 2
    
    db[uid]["step"] = None
    await message.reply_text(f"✅ تم حفظ {step} بنجاح!", reply_markup=main_markup())

# --- تعديل طريقة التشغيل لتجنب خطأ RuntimeError ---
async def main():
    async with app:
        print("--- البوت يعمل الآن بحقوق سالم @hlhrI ---")
        await asyncio.Event().wait()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(main())
    except (KeyboardInterrupt, SystemExit):
        pass
