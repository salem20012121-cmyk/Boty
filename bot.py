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

app = Client("F5R_SHALAL", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# تخزين البيانات مؤقتاً
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
    db[uid] = {"target": None, "senders": [], "sub": "No Subject", "msg": "", "count": 10, "delay": 5, "step": None}
    welcome = (
        "**مرحباً بك في بوت الشد الخارجي 🚀**\n\n"
        "ضبط إعداداتك من الأزرار بالأسفل.\n\n"
        "**Dev: @hlhrI**"
    )
    await message.reply_text(welcome, reply_markup=main_markup())

@app.on_callback_query()
async def callbacks(client, query: CallbackQuery):
    uid = query.from_user.id
    data = query.data
    
    if data == "set_target":
        db[uid]["step"] = "target"
        await query.message.edit_text("🎯 أرسل إيميل الدعم المستهدف:")
    elif data == "add_sender":
        db[uid]["step"] = "sender"
        await query.message.edit_text("📧 أرسل إيميلك وباسورد التطبيقات (email:pass):")
    elif data == "start_burn":
        if not db[uid]["senders"] or not db[uid]["target"]:
            await query.answer("⚠️ بيانات ناقصة!", show_alert=True)
        else:
            asyncio.create_task(burn_process(client, query.message, uid))
    # أضف باقي الأزرار هنا بنفس الطريقة...

async def burn_process(client, msg, uid):
    user = db[uid]
    success, failed = 0, 0
    await msg.edit_text("🚀 جاري بدء العملية...")
    
    for i in range(int(user["count"])):
        try:
            sender = user["senders"][i % len(user["senders"])]
            email_u, pass_u = sender.split(":")
            
            m = MIMEText(user["msg"])
            m["Subject"], m["From"], m["To"] = user["sub"], email_u, user["target"]
            
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as s:
                s.login(email_u, pass_u)
                s.sendmail(email_u, user["target"], m.as_string())
            success += 1
        except:
            failed += 1
            
        status = (
            "**الشد جارٍ...**\n"
            f"✅ نجاح: {success}\n"
            f"❌ فشل: {failed}\n"
            f"🎯 الهدف: `{user['target']}`"
        )
        try: await msg.edit_text(status)
        except: pass
        await asyncio.sleep(int(user["delay"]))

@app.on_message(filters.text & filters.private)
async def handle_input(client, message):
    uid = message.from_user.id
    step = db.get(uid, {}).get("step")
    if step == "target":
        db[uid]["target"] = message.text
        await message.reply_text("✅ تم حفظ الهدف", reply_markup=main_markup())
    elif step == "sender":
        db[uid]["senders"].append(message.text)
        await message.reply_text("✅ تم إضافة الإيميل", reply_markup=main_markup())
    db[uid]["step"] = None

app.run()
