# utils/formatter.py

import datetime
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

GITHUB_LINK = "https://github.com/baytekincan"
UPDATE_INTERVAL_SECONDS = 60

TURKISH_MONTHS = {
    '01': 'Ocak', '02': 'Şubat', '03': 'Mart', '04': 'Nisan',
    '05': 'Mayıs', '06': 'Haziran', '07': 'Temmuz', '08': 'Ağustos',
    '09': 'Eylül', '10': 'Ekim', '11': 'Kasım', '12': 'Aralık'
}

def get_turkish_datetime_str():
    """Returns the current time in 'DD MonthName YYYY HH:MM:SS' format."""
    now = datetime.datetime.now()
    day = now.strftime('%d')
    month_num = now.strftime('%m')
    year = now.strftime('%Y')
    time_str = now.strftime('%H:%M:%S')
    
    turkish_month = TURKISH_MONTHS.get(month_num, month_num)

    return f"{int(day)} {turkish_month} {year} {time_str}"

def format_price_info(gold_type_title, price):
    """Formats a single cached price into a readable string."""
    if "USD" in gold_type_title:
        currency = "USD"
    else:
        currency = "TL"
        
    return f"📈 **{gold_type_title} Alış:** `{price}` {currency}"

def create_main_menu_message():
    """Creates the welcome/main menu message text."""
    return (
        f"🌟 **Altın Takip Botuna Hoş Geldiniz!**\n\n"
        f"Burada **Mynet Finans** kaynaklı güncel altın fiyatlarını **öğrenebilirsiniz**.\n"
        f"Verilerimiz **{UPDATE_INTERVAL_SECONDS} saniyede bir** güncellenmektedir.\n\n"
        f"⚙️ Komutlar\n"
        f"• `/start`: Botu başlatır ve fiyat öğrenme menüsünü getirir.\n"
        f"• `/stop`: Botun size yanıt vermeyi durdurmasını sağlar.\n\n"
        f"Aşağıdan fiyatını **öğrenmek** istediğiniz altın türünü seçin:"
    )

def create_copyright_message():
    """Creates the developer and copyright message."""
    return (
        f"© Tüm hakları saklıdır.\n"
        f"💻 Geliştirici: **Can Baytekin** - [GitHub Profili]({GITHUB_LINK})"
    )

def create_gold_options_keyboard(gold_options):
    """Creates the inline keyboard for gold options."""
    keyboard = []
    
    for display_name, title_value in gold_options.items():
        keyboard.append([InlineKeyboardButton(display_name, callback_data=f'get_type_{title_value}')])

    keyboard.append([InlineKeyboardButton("✨ Hepsini Seç / Tümünü Öğren", callback_data='get_all_prices')])
    keyboard.append([InlineKeyboardButton("❌ Çıkış", callback_data='exit')])
    return InlineKeyboardMarkup(keyboard)

def create_return_to_menu_keyboard():
    """Creates the inline keyboard for returning to the main menu."""
    return InlineKeyboardMarkup([[InlineKeyboardButton("Ana Menüye Dön / Tekrar Öğren 🔄", callback_data='go_main_menu')]])
