import asyncio
import random
import json
import os

from config import TOKEN, ADMIN_ID, PHONE, SESSION
from rubka.asynco import Robot, Message
from rubika import Client


# --------------------------
# فایل‌ها
# --------------------------
RESPONSES_FILE = "responses_async.json"
JOKES_FILE = "jokes_async.json"

bot_status = True   # وضعیت روشن/خاموش ربات


# --------------------------
# بارگذاری پاسخ‌های انسانی
# --------------------------
if os.path.exists(RESPONSES_FILE):
    with open(RESPONSES_FILE, "r", encoding="utf-8") as f:
        human_responses = json.load(f)
else:
    human_responses = {
        "سلام": ["سلام رفیق 😊 خوبی؟", "سلام! چه خبر؟", "درود بر تو 😄 حال و احوال؟"],
        "چطوری": ["خوبم مرسی، تو چطوری؟", "عالی، مرسی که پرسیدی!"],
    }


# --------------------------
# بارگذاری جوک‌ها
# --------------------------
if os.path.exists(JOKES_FILE):
    with open(JOKES_FILE, "r", encoding="utf-8") as f:
        jokes = json.load(f)
else:
    jokes = [
        "میدونی چرا پرستوها پرواز می‌کنن؟ چون اگه پیاده برن خسته میشن.",
        "میدونی چرا ماهی‌ها دست نمی‌دن؟ چون دستشون خیسه.",
        "میدونی اگه فیل بره روی درخت چی میشه؟ یه فیل از روی زمین کم میشه.",
    ]


# --------------------------
# فحش‌ها
# --------------------------
swear_keywords = ["بی‌شعور", "کله‌پوک", "خاک بر سرت", "حمار"]
swear_responses = ["آروم باش داش 😏", "عه رفیق چرا حرصی شدی؟ 😅", "فحش نده ناموساً 😜"]


# --------------------------
# ذخیره‌سازی
# --------------------------
def save_responses():
    with open(RESPONSES_FILE, "w", encoding="utf-8") as f:
        json.dump(human_responses, f, ensure_ascii=False, indent=2)


def save_jokes():
    with open(JOKES_FILE, "w", encoding="utf-8") as f:
        json.dump(jokes, f, ensure_ascii=False, indent=2)


def teach_response(phrase, responses):
    human_responses[phrase.lower()] = responses
    save_responses()


# --------------------------
# بوت اصلی (بات)
# --------------------------
bot = Robot(TOKEN)


@bot.on_message()
async def chat(bot, message: Message):
    global bot_status
    text = (message.text or "").strip()
    user_id = message.sender_id

    if not text:
        return

    # روشن / خاموش
    if user_id == ADMIN_ID:
        if text.lower() == "/off":
            bot_status = False
            await message.reply("🔴 ربات خاموش شد.")
            return

        if text.lower() == "/on":
            bot_status = True
            await message.reply("🟢 ربات روشن شد.")
            return

    if not bot_status:
        return

    # آموزش توسط ادمین
    if user_id == ADMIN_ID and text.startswith("!یادبگیر"):
        try:
            rest = text[len("!یادبگیر"):].strip()
            phrase, responses_str = rest.split(":", 1)
            responses_list = [x.strip() for x in responses_str.split(",") if x.strip()]
            teach_response(phrase, responses_list)
            await message.reply(f"✅ یاد گرفتم: {phrase}")
        except Exception as e:
            await message.reply(f"❌ خطا در آموزش: {e}")
        return

    # افزودن جوک
    if user_id == ADMIN_ID and text.startswith("!جوک"):
        new_joke = text.replace("!جوک", "").strip()
        if len(new_joke) > 3:
            jokes.append(new_joke)
            save_jokes()
            await message.reply("😂 جوک جدید ذخیره شد!")
        else:
            await message.reply("❌ جوک معتبر نیست.")
        return

    # دستور جوک
    if text.lower() in ["جوک", "joke"]:
        await message.reply(random.choice(jokes))
        return

    # جواب انسانی
    for key in human_responses:
        if key in text.lower():
            await message.reply(random.choice(human_responses[key]))
            return

    # فحش‌ها
    for swear in swear_keywords:
        if swear in text.lower():
            await message.reply(random.choice(swear_responses))
            return

    # بلد نبودن
    await message.reply("⚠️ بلد نیستم، ادمین با !یادبگیر یادم بده.")


# --------------------------
# یوزربات (کلاینت)
# --------------------------
app = Client(SESSION, phone=PHONE)
app.start()
@app.on_message()
def handler(message):
    text = message.text

    # حذف با ریپلای
    if text == "حذف" and message.reply_to_message:
        try:
            app.delete_messages(message.chat_id, message.reply_to_message.message_id)
            app.send_message(message.chat_id, "پیام حذف شد ✔️")
        except Exception as e:
            app.send_message(message.chat_id, f"خطا: {e}")

    # حذف تعداد مشخص
    if text.startswith("حذف "):
        try:
            count = int(text.split(" ")[1])
            history = app.get_chat_history(message.chat_id, count=count)
            ids = [msg.message_id for msg in history]
            app.delete_messages(message.chat_id, ids)
            app.send_message(message.chat_id, f"{count} پیام حذف شد ✔️")
        except:
            app.send_message(message.chat_id, "خطا در حذف.")


print("ربات ترکیبی (بات + یوزربات) روشن شد 🔥")


# --------------------------
# اجرای هر دو
# --------------------------
asyncio.run(bot.run())
app.run()