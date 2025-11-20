# main.py

import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, filters
import logging

from controllers.bot_controller import (
    start_command, stop_command, button_handler, go_main_menu, 
    start_background_updater, UPDATE_INTERVAL_SECONDS
)

load_dotenv()
BOT_TOKEN = os.environ.get('BOT_TOKEN')

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

def main():
    if BOT_TOKEN is None:
        print("🔴 ERROR: Please check your .env file and ensure you have entered a valid BOT_TOKEN.")
        return

    start_background_updater() 

    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("stop", stop_command))
    application.add_handler(CallbackQueryHandler(button_handler, pattern='^get_type_|^get_all_prices|^exit'))
    application.add_handler(CallbackQueryHandler(go_main_menu, pattern='^go_main_menu'))

    print(f"✅ Bot is starting... Prices updating every {UPDATE_INTERVAL_SECONDS} seconds.")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()