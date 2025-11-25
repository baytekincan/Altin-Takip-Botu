# main.py

import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler
import logging
from controllers.bot_controller import start_command, stop_command, button_handler, start_background_updater, UPDATE_INTERVAL_SECONDS

load_dotenv()
BOT_TOKEN = os.environ.get("BOT_TOKEN")

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

def main():
    if not BOT_TOKEN:
        print("🔴 HATA: Lütfen .env dosyanızı kontrol edin ve geçerli bir BOT_TOKEN girdiğinizden emin olun.")
        return

    start_background_updater()

    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("stop", stop_command))

    callback_pattern = (
        '^get_type_|^get_all_prices|'
        '^go_main_menu|^go_price_menu|^go_setup_menu|^go_cancel_menu|'
        '^set_notify_freq_|^set_notify_final_|'
        '^confirm_cancel_|^exit_stop'
    )
    app.add_handler(CallbackQueryHandler(button_handler, pattern=callback_pattern))

    print(f"✅ Bot başlatılıyor... Fiyatlar her {UPDATE_INTERVAL_SECONDS} saniyede bir güncelleniyor.")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
