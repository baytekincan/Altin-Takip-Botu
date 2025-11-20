# controllers/bot_controller.py

from telegram import Update, InlineKeyboardMarkup

from services.price_service import get_cached_prices, start_background_updater, GOLD_OPTIONS, UPDATE_INTERVAL_SECONDS
from utils.formatter import (
    create_main_menu_message, create_copyright_message, 
    create_gold_options_keyboard, create_return_to_menu_keyboard,
    format_price_info
)

async def start_command(update: Update, context):
    """Handles the /start command, sends welcome message and menu."""
    
    welcome_message = create_main_menu_message()
    copyright_message = create_copyright_message()
    reply_markup = create_gold_options_keyboard(GOLD_OPTIONS)

    await update.message.reply_text(
        welcome_message,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )
    
    await update.message.reply_text(
        copyright_message, 
        parse_mode='Markdown',
        disable_web_page_preview=True
    )

async def button_handler(update: Update, context):
    """Handles callback queries (button presses)."""
    query = update.callback_query
    await query.answer()

    data = query.data
    response_message = ""
    
    cached_prices, last_update_time, gold_options = get_cached_prices()
    
    if data == 'get_all_prices':
        all_prices_list = []
        for display_name, gold_type_title in gold_options.items():
            price = cached_prices.get(gold_type_title, "Bilgi alınamadı")
            all_prices_list.append(format_price_info(gold_type_title, price)) 

        response_message = (
            f"💰 **Tüm Altın Fiyatları (Anlık Alış)**\n"
            f"🌐 Kaynak: Mynet Finans\n\n"
            f"{' \n'.join(all_prices_list)}\n\n"
            f"⏳ Son Güncelleme: {last_update_time}" 
        )
        
    elif data.startswith('get_type_'):
        gold_type_title = data.replace('get_type_', '')
        price = cached_prices.get(gold_type_title, "Bilgi alınamadı")
        price_info = format_price_info(gold_type_title, price)
        
        response_message = (
            f"💰 **Seçilen Altın Fiyatı (Anlık Alış)**\n"
            f"🌐 Kaynak: Mynet Finans\n\n"
            f"{price_info}\n\n"
            f"⏳ Son Güncelleme: {last_update_time}"
        )
    
    elif data == 'exit':
        await query.edit_message_text(
            "👋 Ana menüden çıkıldı. Fiyatları öğrenmek isterseniz tekrar `/start` komutunu kullanabilirsiniz.",
            parse_mode='Markdown'
        )
        return

    reply_markup = create_return_to_menu_keyboard()

    await query.edit_message_text(
        response_message,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )
    
async def go_main_menu(update: Update, context):
    """Updates the message to show the main menu again."""
    query = update.callback_query
    await query.answer()
    
    # Mesajı ve klavyeyi oluştur
    menu_message = create_main_menu_message()
    reply_markup = create_gold_options_keyboard(GOLD_OPTIONS)
    
    await query.edit_message_text(
        menu_message,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def stop_command(update: Update, context):
    """Handles the /stop command."""
    await update.message.reply_text(
        'Bot hizmeti sonlandırılıyor. Dilediğiniz zaman /start komutu ile yeniden başlatabilirsiniz. 👋'
    )