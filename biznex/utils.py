from decimal import Decimal, InvalidOperation
import urllib.request
import urllib.parse

TELEGRAM_BOT_TOKEN = "7522754240:AAHfCh4pxKW-sD_g2j7OdKQ4DpS5Ci7kpAY"
TELEGRAM_CHAT_ID = "-5568619342"


def send_telegram(text):
    """Admin uchun kerakli barcha hodisalar shu funksiya orqali Telegram guruhga yuboriladi."""
    try:
        url = f"http://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        data = urllib.parse.urlencode({
            'chat_id': TELEGRAM_CHAT_ID,
            'text': text,
            'parse_mode': 'HTML'
        }).encode()
        req = urllib.request.Request(url, data=data)
        urllib.request.urlopen(req, timeout=5)
    except Exception:
        pass


def safe_decimal(value, default='0'):
    """Foydalanuvchi formadan bo'sh yoki noto'g'ri (masalan harf) qiymat yuborsa ham
    xato chiqarmasdan, xavfsiz Decimal qiymat qaytaradi."""
    if value is None:
        value = default
    value = str(value).strip().replace(',', '')
    if not value:
        value = default
    try:
        return Decimal(value)
    except (InvalidOperation, ValueError):
        return Decimal(default)


def safe_int(value, default=0):
    """Foydalanuvchi formadan bo'sh yoki noto'g'ri qiymat yuborsa ham xavfsiz int qaytaradi."""
    if value is None:
        return default
    value = str(value).strip()
    if not value:
        return default
    try:
        return int(float(value))
    except (ValueError, TypeError):
        return default
