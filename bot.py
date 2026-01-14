import os
import json
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# ======================
# TELEGRAM BOT TOKEN
# ======================
TOKEN = os.environ["7761335776:AAH77sm6Vm0hJM-C3H4C9E2HKvce4TeNVbA"]

# ======================
# GOOGLE SHEETS AUTH
# ======================
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

# Ambil Google Service Account dari ENV
service_account_info = json.loads(
    os.environ["GOOGLE_SERVICE_ACCOUNT_JSON"]
)

creds = ServiceAccountCredentials.from_json_keyfile_dict(	
    service_account_info, scope
)

client = gspread.authorize(creds)

# Tukar kepada KEY Google Sheet cikgu
sheet = client.open_by_key(
    "13H2dd939B_DVphoeYWvdJFCTscgmviG9RPIZS8cankU"
).sheet1

# ======================
# SIMPAN STATUS USER
# ======================
user_waiting_pin = set()

# ======================
# /start COMMAND
# ======================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_waiting_pin.add(update.effective_user.id)
    await update.message.reply_text(
        "👋 Assalamualaikum.\n"
        "Sila masukkan PIN anda:"
    )

# ======================
# TERIMA PIN
# ======================
async def terima_pin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id not in user_waiting_pin:
        return

    pin = update.message.text.strip()
    data = sheet.get_all_records()

    for row in data:
        if str(row["PIN"]).strip() == pin:
            user_waiting_pin.remove(user_id)
            await update.message.reply_text(
                "✅ Pengesahan berjaya\n\n"
                f"👤 Nama: {row['NAMA MURID']}\n"
                f"🏫 Kelas: {row['Kelas']}\n"
                f"📧 ID DELIMa: {row['ID DELIMA']}"
            )
            return

    await update.message.reply_text(
        "❌ PIN tidak sah.\n"
        "Sila cuba lagi."
    )

# ======================
# RUN BOT
# ======================
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, terima_pin)
    )

    print("🤖 Bot sedang berjalan...")
    app.run_polling()

if name == "main":
    main()