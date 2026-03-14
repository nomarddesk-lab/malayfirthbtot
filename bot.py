import os
import threading
from datetime import datetime
from flask import Flask
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

# --- Pelayan Web untuk Render.com (Health Check) ---
app = Flask(__name__)

@app.route('/')
def health_check():
    return "Cikgu Gadget Bot sedang aktif! Jom jaga barang rumah!", 200

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# --- Kandungan Bot (Tips Penjagaan Gadget dalam Bahasa Melayu) ---

LEARNING_CONTENT = [
    # Hari 1: Penjagaan Bateri (Telefon & Laptop)
    "📱 *Hari 1: Rahsia Bateri Tahan Bertahun-tahun*\n\n"
    "Ramai orang silap cara cas telefon! Ini tips supaya bateri tak cepat 'kembung'.\n\n"
    "*Tips Utama:*\n"
    "- *Jangan Cas Semalaman:* Elakkan cas 100% terlalu lama. Sebaiknya kekalkan antara 20% hingga 80%.\n"
    "- *Suhu Panas:* Jangan tinggal telefon dalam kereta yang panas atau cas sambil main 'game' berat.\n"
    "- *Gunakan Pengecas Original:* Pengecas murah boleh merosakkan litar dalaman gajet.\n\n"
    "*Tips Cikgu:* Kalau tak guna laptop untuk masa lama, jangan biar bateri 0%. Cas sampai 50% sebelum simpan.",

    # Hari 2: Peralatan Dapur (Peti Sejuk & Microwave)
    "❄️ *Hari 2: Peti Sejuk & Microwave*\n\n"
    "Barang dapur kalau rosak, kos baiki mahal! Jom buat 'maintenance' sendiri.\n\n"
    "*Peti Sejuk:*\n"
    "- *Jarakkan dari Dinding:* Pastikan ada ruang udara (sekurang-kurangnya 10cm) di belakang peti sejuk supaya motor tak panas.\n"
    "- *Jangan Sumbat Terlalu Penuh:* Udara sejuk perlu mengalir untuk kekalkan suhu.\n\n"
    "*Microwave:*\n"
    "- *Lap Serta-merta:* Sisa makanan yang melekat akan menyerap tenaga gelombang dan boleh merosakkan dinding microwave lama-kelamaan.",

    # Hari 3: Air-Cond (Pendingin Udara)
    "🌬️ *Hari 3: Air-Cond Sejuk Macam Baru*\n\n"
    "Air-cond tak sejuk? Jangan terus panggil tukang, periksa ni dulu!\n\n"
    "*Penjagaan Rutin:*\n"
    "- *Cuci Penapis (Filter):* Buat setiap 2 minggu sekali. Habuk yang tebal memaksa enjin bekerja lebih keras (bil elektrik pun naik!).\n"
    "- *Suhu Ideal:* Tetapkan suhu antara 23°C - 25°C. Suhu terlalu rendah (16°C) memendekkan jangka hayat kompresor.\n\n"
    "*Tips:* Gunakan fungsi 'Dry Mode' jika cuaca lembap untuk kurangkan beban pada mesin.",
]

QUIZ_DATA = [
    {
        "question": "Berapakah peratusan bateri yang terbaik untuk dikekalkan supaya tahan lama?",
        "options": ["0% hingga 100%", "20% hingga 80%", "Sentiasa 100%"],
        "correct": 1
    },
    {
        "question": "Mengapakah peti sejuk perlu diletakkan jauh sedikit dari dinding?",
        "options": ["Supaya senang nak cuci", "Untuk pengaliran udara haba motor", "Supaya nampak cantik"],
        "correct": 1
    },
    {
        "question": "Berapa kerapkah penapis (filter) air-cond perlu dicuci?",
        "options": ["Setiap 2 minggu", "Setahun sekali", "Bila air-cond dah rosak"],
        "correct": 0
    }
]

# --- Logik Bot ---
user_progress = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in user_progress:
        user_progress[user_id] = {"day": 0, "quiz_day": 0, "last_learned_date": None}
    
    keyboard = [
        ["Belajar Tip Gadget 🛠️", "Kuiz Gadget 🧠"],
        ["Rehat Dulu ☕"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    welcome_text = (
        f"Selamat Datang ke *Cikgu Gadget Gari*! 👨‍🔧🏠\n\n"
        "Saya akan bantu anda jaga gajet dan barang elektrik rumah supaya tahan bertahun-tahun.\n"
        "Pilih menu di bawah untuk mula belajar tips hari ini."
    )
    await update.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode='Markdown')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text
    
    if user_id not in user_progress:
        user_progress[user_id] = {"day": 0, "quiz_day": 0, "last_learned_date": None}

    if text == "Belajar Tip Gadget 🛠️":
        current_day = user_progress[user_id]["day"]
        today = str(datetime.now().date())
        
        if user_progress[user_id]["last_learned_date"] == today:
            await update.message.reply_text("Hebat! Anda dah belajar tips hari ini. Datang lagi esok untuk tips gajet lain ya! 💡")
            return

        if current_day < len(LEARNING_CONTENT):
            await update.message.reply_text(LEARNING_CONTENT[current_day], parse_mode='Markdown')
            user_progress[user_id]["day"] += 1
            user_progress[user_id]["last_learned_date"] = today
        else:
            await update.message.reply_text("Tahniah! Anda kini 'Master Gadget'. Tunggu kemas kini untuk peralatan lain!")

    elif text == "Kuiz Gadget 🧠":
        current_quiz_idx = user_progress[user_id]["quiz_day"]
        
        if current_quiz_idx < len(QUIZ_DATA):
            q = QUIZ_DATA[current_quiz_idx]
            buttons = [[InlineKeyboardButton(opt, callback_data=f"quiz_{idx}")] for idx, opt in enumerate(q["options"])]
            reply_markup = InlineKeyboardMarkup(buttons)
            await update.message.reply_text(f"Soalan Kuiz Penjagaan:\n\n{q['question']}", reply_markup=reply_markup)
        else:
            await update.message.reply_text("Anda telah menjawab semua kuiz gajet! Barang rumah anda pasti selamat. 🏆")

    elif text == "Rehat Dulu ☕":
        await update.message.reply_text("Sambil rehat tu, jangan lupa tutup suis barang elektrik yang tak guna ya! Jimat bil! 👋")

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()
    
    current_quiz_idx = user_progress[user_id]["quiz_day"]
    if current_quiz_idx >= len(QUIZ_DATA):
        return

    selected_option = int(query.data.split("_")[1])
    if selected_option == QUIZ_DATA[current_quiz_idx]["correct"]:
        feedback = "Betul! Anda memang bijak menjaga harta benda. ✅\n\n"
    else:
        feedback = "Alamak, salah tu! Tak apa, lepas ni boleh perbaiki. ❌\n\n"
    
    feedback += "Penjagaan yang baik mengelakkan pembaziran wang! 💰"
    user_progress[user_id]["quiz_day"] += 1
    await query.edit_message_text(text=feedback)

if __name__ == '__main__':
    threading.Thread(target=run_flask, daemon=True).start()
    
    TOKEN = os.environ.get("TELEGRAM_TOKEN")
    if not TOKEN:
        print("RALAT: TELEGRAM_TOKEN tidak dijumpai.")
        exit(1)
    
    print("Memulakan Cikgu Gadget Bot...")
    application = ApplicationBuilder().token(TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    application.add_handler(CallbackQueryHandler(handle_callback))
    
    application.run_polling()
