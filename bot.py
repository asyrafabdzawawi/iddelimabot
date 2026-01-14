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
# /start
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

    matched_rows = []

    # Cari SEMUA murid dengan PIN sama
    for row in data:
        if str(row["PIN"]).strip().zfill(len(pin)) == pin:
            matched_rows.append(row)

    # Jika ada padanan
    if matched_rows:
        user_waiting_pin.remove(user_id)

        message = "✅ Pengesahan berjaya\n\n"

        # Papar setiap murid (format asal, diulang)
        for row in matched_rows:
            message += (
                f"👤 Nama: {row['NAMA MURID']}\n"
                f"🏫 Kelas: {row['KELAS']}\n"
                f"📧 ID DELIMa: {row['ID DELIMA']}\n\n"
            )

        # Jika PIN dikongsi
        if len(matched_rows) > 1:
            message += (
                f"⚠️ PIN ini dikongsi oleh {len(matched_rows)} orang murid."
            )

        await update.message.reply_text(message)
        return

    # Jika tiada padanan
    await update.message.reply_text(
        "❌ PIN tidak sah.\nSila cuba lagi."
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