import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import random
import time
import os

# قراءة البيانات من إعدادات السيرفر (Environment Variables)
BOT_TOKEN = os.getenv("BOT_TOKEN") 
ADMIN_ID = int(os.getenv("ADMIN_IDS", "6421333576"))
CHANNEL_USERNAME = os.getenv("REQUIRED_CHANNEL", "@s11r6")

bot = telebot.TeleBot(BOT_TOKEN)

# تخزين المستخدمين في الذاكرة
waiting_users = []
active_chats = {}
chat_times = {}

# اقتباسات الافتتاح والختام
opening_quotes = [
    "🌙 «ابدأ الحديث، فما خُلق الكلام إلا ليريح القلب.»",
    "🌙 «قد يكون الكلام دواءً حين يصعب الصمت.»"
]
closing_quotes = [
    "💭 «كلّ لقاءٍ يترك أثرًا، ولو كان عابرًا.»",
    "💭 «ربّ كلمةٍ خفّفت عن قلبٍ ما أثقل الجبال.»",
    "💭 «ليس كلّ من يرحل، يُنسى.»"
]

def check_subscription(user_id):
    try:
        member = bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False

def start_markup():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🔮 ابحث عن شريك", callback_data="find"))
    return markup

@bot.message_handler(commands=["start"])
def start(msg):
    user_id = msg.chat.id
    if not check_subscription(user_id):
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("📢 اشترك في القناة", url=f"https://t.me/{CHANNEL_USERNAME[1:]}"))
        bot.send_message(user_id, "🔔 يجب الاشتراك بقناة البوت أولاً:", reply_markup=markup)
        return
    bot.send_message(user_id, "🌙 أهلاً بك في <b>Vently — نَفَس</b>\n"
                              "اضغط أدناه لبدء محادثة مجهولة لمدة 15 دقيقة 🌌",
                     reply_markup=start_markup(), parse_mode="HTML")

@bot.callback_query_handler(func=lambda call: call.data == "find")
def find_partner(call):
    user_id = call.message.chat.id
    if user_id in active_chats:
        bot.answer_callback_query(call.id, "أنت في محادثة حالياً 🌙")
        return
    if waiting_users and waiting_users[0] != user_id:
        partner_id = waiting_users.pop(0)
        active_chats[user_id] = partner_id
        active_chats[partner_id] = user_id
        chat_times[user_id] = time.time()
        chat_times[partner_id] = time.time()

        quote = random.choice(opening_quotes)
        bot.send_message(user_id, f"{quote}\n\n🎧 تم العثور على شريك! يمكنك البدء الآن 💬")
        bot.send_message(partner_id, f"{quote}\n\n🎧 تم العثور على شريك! يمكنك البدء الآن 💬")
    else:
        waiting_users.append(user_id)
        bot.send_message(user_id, "⏳ جاري البحث عن شريك ...")

@bot.message_handler(func=lambda m: True)
def relay_message(msg):
    sender = msg.chat.id
    if sender in active_chats:
        receiver = active_chats[sender]
        bot.send_message(receiver, msg.text)
    else:
        bot.send_message(sender, "💭 استخدم الأمر /start للبدء.")

def end_chat(user_id):
    if user_id in active_chats:
        partner_id = active_chats.pop(user_id)
        active_chats.pop(partner_id, None)
        quote = random.choice(closing_quotes)
        for uid in [user_id, partner_id]:
            bot.send_message(uid, f"{quote}\n\n🔁 ابدأ من جديد 🔮", reply_markup=start_markup())

@bot.message_handler(commands=["end"])
def cmd_end(msg):
    end_chat(msg.chat.id)

print("🚀 Vently — نَفَس v2 يعمل الآن...")
bot.infinity_polling()
