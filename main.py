import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import random

TOKEN = "8920352062:AAGEBlXF6HRQKr_D7lbOW_QrAKXvulrvjPw"
bot = telebot.TeleBot(TOKEN)

MOCK_QUESTIONS = [
    {"q": "Ich freue mich ___ den Urlaub nächsten Monat.", "o": ["auf", "über", "für"], "c": "auf", "e": "نستخدم auf للمستقبل."},
    {"q": "Was bedeutet 'die Gelegenheit'?", "o": ["المناسبة", "الفرصة", "النصيحة"], "c": "الفرصة", "e": "تعني الفرصة."},
    {"q": "Wenn ich mehr Zeit ___, würde ich Deutsch lernen.", "o": ["habe", "hätte", "hatte"], "c": "hätte", "e": "صيغة تمني للحاضر."},
    {"q": "Er hat die Prüfung bestanden, ___ er viel gelernt hat.", "o": ["weil", "deshalb", "obwohl"], "c": "weil", "e": "لأنها تربط جملة سببية."},
    {"q": "Was bedeutet 'abhängen von'?", "o": ["يعتمد على", "يهتم بـ", "يتحدث عن"], "c": "يعتمد على", "e": "تعني يعتمد على."}
]

user_sessions = {}

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    text = "🤖 **مرحباً بك في بوت الألمانية الخارق المستمر 24 ساعة!**\n\n🔹 `/exam` - دليل ونماذج غوته B1\n🔹 `/mock` - بدء امتحان تجريبي\n🔹 `/challenge` - التحديات ولوحة الصدارة"
    bot.reply_to(message, text, parse_mode="Markdown")

@bot.message_handler(commands=['exam'])
def send_exam_info(message):
    text = "📝 **دليل ومصادر امتحان Goethe B1 الرسمي:**\n\nاضغط على الروابط للتحميل والتدريب:"
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("📄 نماذج معهد غوته الرسمية", url="https://www.goethe.de/de/spr/kup/prf/prf/gzb1/ueb.html"))
    markup.add(InlineKeyboardButton("🎯 تدريبات DW Nicos Weg B1", url="https://learngerman.dw.com/de/nicos-weg/c-36519789"))
    bot.send_message(message.chat.id, text, reply_markup=markup, parse_mode="Markdown")

@bot.message_handler(commands=['mock'])
def start_mock(message):
    uid = message.from_user.id
    user_sessions[uid] = {"qs": random.sample(MOCK_QUESTIONS, 5), "idx": 0, "score": 0, "wrongs": []}
    bot.send_message(message.chat.id, "⏱ **بدأ الاختبار التجريبي (5 أسئلة)!**")
    send_q(message.chat.id, uid)

def send_q(chat_id, uid):
    sess = user_sessions.get(uid)
    if not sess or sess["idx"] >= 5:
        score, wrongs = sess["score"], sess["wrongs"] if sess else (0, [])
        res = f"🏁 **انتهى الاختبار!**\n\nنتيجتك: *{score} من 5*\n"
        if wrongs:
            res += "\n🧠 **مراجعة الأخطاء:**"
            for w in wrongs: res += f"\n• {w['q']}\n💡 الصح: *{w['c']}* ({w['e']})"
        bot.send_message(chat_id, res, parse_mode="Markdown")
        user_sessions.pop(uid, None)
        return
    q = sess["qs"][sess["idx"]]
    markup = InlineKeyboardMarkup()
    for o in q["o"]: markup.add(InlineKeyboardButton(o, callback_data=f"m_{uid}_{o}"))
    bot.send_message(chat_id, f"❓ **السؤال {sess['idx']+1}:**\n{q['q']}", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("m_"))
def handle_ans(call):
    _, uid, ans = call.data.split("_")
    uid = int(uid)
    if call.from_user.id != uid: return
    sess = user_sessions.get(uid)
    if not sess: return
    q = sess["qs"][sess["idx"]]
    if ans == q["c"]:
        sess["score"] += 1
        bot.answer_callback_query(call.id, "✅ صح!")
    else:
        sess["wrongs"].append({"q": q["q"], "c": q["c"], "e": q["e"]})
        bot.answer_callback_query(call.id, f"❌ خطأ! الصح: {q['c']}", show_alert=True)
    sess["idx"] += 1
    bot.delete_message(call.message.chat.id, call.message.message_id)
    send_q(call.message.chat.id, uid)

@bot.message_handler(commands=['challenge'])
def send_challenge(message):
    text = "🏆 **لوحة صدارة شعبة التدريب:**\n\n🥇 الأول: *عضيد* — 1250 نقطة ⚡\n🥈 الثاني: *محمد* — 980 نقطة\n🥉 الثالث: *أحمد* — 710 نقطة"
    bot.reply_to(message, text, parse_mode="Markdown")

print("🤖 البوت يعمل بنجاح...")
bot.infinity_polling(timeout=10, long_polling_timeout=5)
