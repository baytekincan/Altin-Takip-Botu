# utils/formatter.py

import datetime
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

UPDATE_INTERVAL_SECONDS = 60
GITHUB_LINK = "https://github.com/baytekincan"

NOTIFICATION_FREQUENCIES = {
    "5 Dakika": 300,
    "15 Dakika": 900,
    "30 Dakika": 1800,
    "1 Saat": 3600
}

TURKISH_MONTHS = {
    '01': 'Ocak', '02': 'Şubat', '03': 'Mart', '04': 'Nisan',
    '05': 'Mayıs', '06': 'Haziran', '07': 'Temmuz', '08': 'Ağustos',
    '09': 'Eylül', '10': 'Ekim', '11': 'Kasım', '12': 'Aralık'
}

MAIN_MENU_BUTTONS = {
    "💰 Anlık Altın Fiyatı Öğren": "go_price_menu",
    "🔔 Periyodik Bildirim Ayarla": "go_setup_menu",
    "👋 Botu Durdur": "exit_stop"
}

def get_turkish_datetime_str():
    now = datetime.datetime.now()
    day = now.strftime('%d')
    month_num = now.strftime('%m')
    year = now.strftime('%Y')
    time_str = now.strftime('%H:%M:%S')
    
    turkish_month = TURKISH_MONTHS.get(month_num, month_num)
    return f"{int(day)} {turkish_month} {year} {time_str}"

def format_price_info(gold_type_title, price):
    currency = "USD" if "USD" in gold_type_title else "TL"
    return f"📈 **{gold_type_title} Alış:** `{price}` {currency}"

def create_main_menu_message():
    return (
        f"🌟 **Altın Takip Botuna Hoş Geldiniz!**\n\n"
        f"Burada **Mynet Finans** kaynaklı güncel altın fiyatlarını **öğrenebilirsiniz**.\n"
        f"Verilerimiz **{UPDATE_INTERVAL_SECONDS} saniyede bir** güncellenmektedir.\n\n"
        f"⚙️ Komutlar\n"
        f"• `/start`: Botu başlatır ve fiyat öğrenme menüsünü getirir.\n"
        f"• `/stop`: Botun size yanıt vermeyi durdurmasını sağlar.\n\n"
        f"⚠️ **Not:** Botun size bildirimleri düzenli gönderebilmesi için, "
        f"bildirim ayarınızı yaptıktan sonra botu durdurmamanız gerekir.\n\n"
    )

def create_copyright_message():
    return f"© Tüm hakları saklıdır.\n💻 Geliştirici: Can Baytekin - {GITHUB_LINK}"

def create_main_menu_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text, callback_data=data)]
        for text, data in MAIN_MENU_BUTTONS.items()
    ]
    return InlineKeyboardMarkup(buttons)

def create_price_inquiry_keyboard(gold_options: dict) -> InlineKeyboardMarkup:
    buttons = []
    for display_name, gold_type_title in gold_options.items():
        buttons.append([InlineKeyboardButton(f"🥇 {display_name}", callback_data=f"get_type_{gold_type_title}")])
    buttons.append([InlineKeyboardButton("📊 Tüm Fiyatları Göster", callback_data="get_all_prices")])
    buttons.append([InlineKeyboardButton("⬅️ Ana Menüye Dön", callback_data="go_main_menu")])
    return InlineKeyboardMarkup(buttons)

def create_price_return_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton("🔙 Geri", callback_data="go_price_menu")],
        [InlineKeyboardButton("🏠 Ana Menüye Dön", callback_data="go_main_menu")]
    ]
    return InlineKeyboardMarkup(buttons)

def create_frequency_keyboard() -> InlineKeyboardMarkup:
    buttons = []
    freq_buttons = []
    for label, seconds in NOTIFICATION_FREQUENCIES.items():
        freq_buttons.append(
            InlineKeyboardButton(f"⏰ {label}", callback_data=f"set_notify_freq_{seconds}")
        )
    buttons.append([freq_buttons[0], freq_buttons[1]])
    buttons.append([freq_buttons[2], freq_buttons[3]])
    buttons.append([
        InlineKeyboardButton("🚫 Bildirim İptal Et/Kontrol Et", callback_data="go_cancel_menu"),
        InlineKeyboardButton("🏠 Ana Menüye Dön", callback_data="go_main_menu")
    ])
    return InlineKeyboardMarkup(buttons)

def create_notification_gold_keyboard(gold_options: dict, frequency_seconds: str) -> InlineKeyboardMarkup:
    buttons = []
    for display_name, gold_type_title in gold_options.items():
        buttons.append([InlineKeyboardButton(f"🥇 {display_name}", callback_data=f"set_notify_final_{frequency_seconds}_{gold_type_title}")])
    buttons.append([InlineKeyboardButton("⬅️ Ana Menüye Dön", callback_data="go_main_menu")])
    return InlineKeyboardMarkup(buttons)

def create_job_list_keyboard(active_jobs: list) -> InlineKeyboardMarkup:
    buttons = []
    if active_jobs:
        for job in active_jobs:
            button_text = f"{job['gold_type']} ({job['frequency']}) - İPTAL ET"
            buttons.append([InlineKeyboardButton(button_text, callback_data=f"confirm_cancel_{job['job_name']}")])
    else:
        buttons.append([InlineKeyboardButton("Aktif bildiriminiz bulunmamaktadır.", callback_data="ignore")])
    buttons.append([InlineKeyboardButton("⬅️ Ana Menüye Dön", callback_data="go_main_menu")])
    return InlineKeyboardMarkup(buttons)

def create_no_alert_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton("🔔 Yeni Bildirim Ayarla", callback_data="go_setup_menu")],
        [InlineKeyboardButton("⬅️ Ana Menüye Dön", callback_data="go_main_menu")]
    ]
    return InlineKeyboardMarkup(buttons)

def create_return_to_menu_keyboard() -> InlineKeyboardMarkup:
    buttons = [[InlineKeyboardButton("⬅️ Ana Menüye Dön", callback_data="go_main_menu")]]
    return InlineKeyboardMarkup(buttons)