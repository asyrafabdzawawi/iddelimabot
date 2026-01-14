import os
import json
from telegram import Update, ReplyKeyboardMarkup
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
TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]

# ======================
# GOOGLE SHEETS AUTH
# ======================
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

service_account_info = json.loads(
    os.environ["GOOGLE_SERVICE_ACCOUNT_JSON"]
)

creds = ServiceAccountCredentials.from_json_keyfile_dict(
    service_account_info, scope
)

client = gspread.authorize(creds)

sheet = client.open_by_key(
    "13H2dd939B_DVphoeYWvdJFCTscgmviG9RPIZS8cankU"
).sheet1

# ======================
# SIMPAN STATUS USER
# ======================
user_waiting_pin = set()

# ======================
# KEYBOARD BUTTON
# ======================
start_keyboard = ReplyKeyboardMarkup(
    [["🔍 SEMAK ID"]],
    resize_keyboard=True
)

# ======================
# /start ATAU BUTANG
# ======================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_waiting_pin.add(update.effective_user.id)

    await update.message.reply_text(
        "👋 Assalamualaikum.\n"
        "Sila masukkan PIN anda:",
        reply_markup=start_keyboard
    )

# ======================
# TERIMA PIN
# ======================
async def terima_pin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()

    # Jika tekan butang SEMAK PIN
    if text == "🔍 SEMAK PIN":
        user_waiting_pin.add(user_id)
        await update.message.reply_text(
            "Sila masukkan PIN anda:",
            reply_markup=start_keyboard
        )
        return

    if user_id not in user_waiting_pin:
        return

    pin = text
    data = sheet.get_all_records()

    matched_rows = []

    # Cari SEMUA murid dengan PIN sama (support 0 depan)
    for row in data:
        if str(row["PIN"]).strip().zfill(len(pin)) == pin:
            matched_rows.append(row)

    # Jika jumpa
    if matched_rows:
        user_waiting_pin.remove(user_id)

        message = "✅ Pengesahan berjaya\n\n"

        for row in matched_rows:
            message += (
                f"👤 Nama: {row['NAMA MURID']}\n"
                f"🏫 Kelas: {row['KELAS']}\n"
                f"📧 ID DELIMa: {row['ID DELIMA']}\n\n"
            )

        if len(matched_rows) > 1:
            message += (
                f"⚠️ PIN ini dikongsi oleh {len(matched_rows)} orang murid."
            )

        await update.message.reply_text(
            message,
            reply_markup=start_keyboard
        )
        return

    # Jika PIN tidak sah
    await update.message.reply_text(
        "❌ PIN tidak sah.\nSila cuba lagi.",
        reply_markup=start_keyboard
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

if __name__ == "__main__":
    main()