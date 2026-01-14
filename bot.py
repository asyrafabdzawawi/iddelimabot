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