# controllers/bot_controller.py

import logging
from telegram import Update
from telegram.ext import ContextTypes
from services.price_service import get_cached_prices, start_background_updater, GOLD_OPTIONS, UPDATE_INTERVAL_SECONDS
from utils.formatter import (
    create_main_menu_message, create_copyright_message,
    format_price_info, create_main_menu_keyboard, create_price_inquiry_keyboard,
    create_frequency_keyboard, create_notification_gold_keyboard, create_job_list_keyboard,
    create_no_alert_keyboard, create_return_to_menu_keyboard, create_price_return_keyboard,
    NOTIFICATION_FREQUENCIES
)

logger = logging.getLogger(__name__)

async def send_periodic_notification(context: ContextTypes.DEFAULT_TYPE):
    job = context.job
    gold_type_title = job.data[0]
    chat_id = job.chat_id

    cached_prices, last_update_time, _ = get_cached_prices()
    price = cached_prices.get(gold_type_title, "Bilgi alınamadı")
    price_info = format_price_info(gold_type_title, price)

    notification_message = (
        f"🔔 **{gold_type_title} Periyodik Fiyat Bilgisi**\n"
        f"———————————————\n"
        f"{price_info}\n"
        f"⏳ Son Güncelleme: {last_update_time}"
    )

    await context.bot.send_message(chat_id=chat_id, text=notification_message, parse_mode='Markdown')

def remove_job_if_exists(job_name: str, context: ContextTypes.DEFAULT_TYPE) -> bool:
    current_jobs = context.job_queue.get_jobs_by_name(job_name)
    if not current_jobs:
        return False
    for job in current_jobs:
        job.schedule_removal()
    return True

def get_all_active_jobs(chat_id: int, context: ContextTypes.DEFAULT_TYPE) -> list:
    active_jobs_info = []
    for job in context.job_queue.jobs():
        job_name = job.name
        if job_name and job_name.startswith(f"notify_{chat_id}_"):
            try:
                parts = job_name.split('_')
                frequency_seconds = int(parts[-2])
                gold_type_title = parts[-1]
                frequency_label = next(
                    (label for label, sec in NOTIFICATION_FREQUENCIES.items() if sec == frequency_seconds),
                    f"{frequency_seconds} sn."
                )
                gold_display_name = next(
                    (name for name, title in GOLD_OPTIONS.items() if title == gold_type_title),
                    gold_type_title
                )
                active_jobs_info.append({
                    'gold_type': gold_display_name,
                    'frequency': frequency_label,
                    'job_name': job_name
                })
            except (IndexError, ValueError) as e:
                logger.error(f"Job adı ayrıştırılamadı: {job_name}. Hata: {e}")
                continue
    return active_jobs_info

async def start_command(update: Update, context):
    welcome_message = create_main_menu_message()
    reply_markup = create_main_menu_keyboard()
    await update.message.reply_text(welcome_message, reply_markup=reply_markup, parse_mode='Markdown')

    copyright_message = create_copyright_message()
    await update.message.reply_text(
        copyright_message, parse_mode='Markdown', disable_web_page_preview=True
    )

async def stop_command(update: Update, context):
    chat_id = None
    if update.message:
        chat_id = update.message.chat_id
    elif update.callback_query:
        chat_id = update.callback_query.message.chat_id

    if chat_id:
        active_jobs = get_all_active_jobs(chat_id, context)
        for job_info in active_jobs:
            remove_job_if_exists(job_info['job_name'], context)

        if update.message:
            await update.message.reply_text(
                'Bot hizmeti ve tüm aktif bildirimler sonlandırılıyor. Dilediğiniz zaman /start komutu ile yeniden başlatabilirsiniz. 👋'
            )
    else:
        logger.error("stop_command çağrılırken chat_id bulunamadı.")

async def button_handler(update: Update, context):
    query = update.callback_query
    await query.answer()
    data = query.data
    response_message = ""
    reply_markup = None

    cached_prices, last_update_time, gold_options = get_cached_prices()
    chat_id = query.message.chat_id

    if data == 'go_main_menu':
        menu_message = create_main_menu_message()
        reply_markup = create_main_menu_keyboard()
        await query.edit_message_text(menu_message, reply_markup=reply_markup, parse_mode='Markdown')
        return

    elif data == 'go_price_menu':
        menu_message = "💰 **Anlık Fiyat Öğrenme**\n\nLütfen fiyatını hemen görmek istediğiniz altın türünü seçin:"
        reply_markup = create_price_inquiry_keyboard(GOLD_OPTIONS)
        await query.edit_message_text(menu_message, reply_markup=reply_markup, parse_mode='Markdown')
        return

    elif data.startswith('get_type_'):
        gold_type_title = data.replace('get_type_', '')
        price = cached_prices.get(gold_type_title, "Bilgi alınamadı")
        price_info = format_price_info(gold_type_title, price)
        response_message = (
            "💰 **Seçilen Altın Fiyatı (Anlık Alış)**\n"
            "🌐 Kaynak: Mynet Finans\n\n"
            f"{price_info}\n\n"
            f"⏳ Son Güncelleme: {last_update_time}"
        )
        reply_markup = create_price_return_keyboard()

    elif data == 'get_all_prices':
        all_prices_list = [format_price_info(t, cached_prices.get(t, "Bilgi alınamadı")) for t in gold_options.values()]
        all_prices_text = "\n".join(all_prices_list)
        response_message = (
            "💰 **Tüm Altın Fiyatları (Anlık Alış)**\n"
            "🌐 Kaynak: Mynet Finans\n\n"
            f"{all_prices_text}\n\n"
            f"⏳ Son Güncelleme: {last_update_time}"
        )
        reply_markup = create_price_return_keyboard()

    elif data == 'go_setup_menu':
        menu_message = "🔔 **Periyodik Bildirim Ayarı**\n\nLütfen önce bildirim almak istediğiniz **sıklığı** seçin:"
        reply_markup = create_frequency_keyboard()
        await query.edit_message_text(menu_message, reply_markup=reply_markup, parse_mode='Markdown')
        return

    elif data.startswith('set_notify_freq_'):
        frequency_seconds = data.replace('set_notify_freq_', '')
        menu_message = "✅ Sıklık ayarlandı. Lütfen şimdi **takip etmek** istediğiniz altın türünü seçin:"
        reply_markup = create_notification_gold_keyboard(GOLD_OPTIONS, frequency_seconds)
        await query.edit_message_text(menu_message, reply_markup=reply_markup, parse_mode='Markdown')
        return

    elif data.startswith('set_notify_final_'):
        parts = data.split('_')
        frequency_seconds = int(parts[3])
        gold_type_title = parts[4]

        job_name = f"notify_{chat_id}_{frequency_seconds}_{gold_type_title}"
        remove_job_if_exists(job_name, context)

        context.job_queue.run_repeating(
            send_periodic_notification, interval=frequency_seconds, first=1,
            chat_id=chat_id, name=job_name, data=[gold_type_title]
        )

        frequency_label = next(
            (label for label, sec in NOTIFICATION_FREQUENCIES.items() if sec == frequency_seconds),
            f"{frequency_seconds} sn."
        )

        response_message = (
            f"🎉 **Yeni Bildirim Başarıyla Ayarlandı!**\n\n"
            f"Altın: **{gold_type_title}**\n"
            f"Sıklık: **{frequency_label}'te bir**\n\n"
            f"İlk bildirimi şimdi alacaksınız. Birden fazla bildirim ayarlayabilirsiniz."
        )
        reply_markup = create_return_to_menu_keyboard()

    elif data == 'go_cancel_menu':
        active_jobs = get_all_active_jobs(chat_id, context)
        if active_jobs:
            response_message = f"🚫 **Aktif Bildirimleriniz ({len(active_jobs)} adet):**\n\nLütfen iptal etmek istediğiniz bildirimi seçin:"
            reply_markup = create_job_list_keyboard(active_jobs)
        else:
            response_message = "🤷‍♂️ **Aktif Bildirim Bulunamadı.**\n\nYeni bir bildirim ayarlayabilirsiniz."
            reply_markup = create_no_alert_keyboard()

    elif data.startswith('confirm_cancel_'):
        job_name_to_remove = data.replace('confirm_cancel_', '')
        if remove_job_if_exists(job_name_to_remove, context):
            response_message = "✅ **Bildirim Başarıyla İptal Edildi.**"
        else:
            response_message = "🚫 İptal etmeye çalıştığınız bildirim zaten aktif değildi."
        reply_markup = create_return_to_menu_keyboard()

    elif data == 'exit_stop':
        await stop_command(update, context)
        await query.edit_message_text(
            "👋 Bot durduruldu ve varsa tüm aktif bildirimleriniz iptal edildi. Tekrar `/start` komutunu kullanabilirsiniz.",
            parse_mode='Markdown'
        )
        return

    if response_message:
        await query.edit_message_text(response_message, reply_markup=reply_markup, parse_mode='Markdown')
