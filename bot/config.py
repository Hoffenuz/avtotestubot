import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
QUESTIONS_FILE = BASE_DIR / "600.json"
DB_PATH = BASE_DIR / "data" / "bot.db"

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
IMAGE_BASE_URL = os.getenv(
    "IMAGE_BASE_URL", "https://www.avtotestu.uz/images"
).rstrip("/")

WEBAPP_URL = os.getenv("WEBAPP_URL", "https://avtotestu.uz").rstrip("/")
PRO_CONTACT = os.getenv("PRO_CONTACT", "@avtotestu_ad")

DAILY_QUIZ_HOUR = int(os.getenv("DAILY_QUIZ_HOUR", "9"))
DAILY_QUIZ_MINUTE = int(os.getenv("DAILY_QUIZ_MINUTE", "0"))
DAILY_QUESTIONS_COUNT = int(os.getenv("DAILY_QUESTIONS_COUNT", "5"))

EXAM_QUESTIONS_COUNT = int(os.getenv("EXAM_QUESTIONS_COUNT", "20"))
QUICK_QUIZ_COUNT = int(os.getenv("QUICK_QUIZ_COUNT", "10"))
QUIZ_QUESTION_TIMEOUT = int(os.getenv("QUIZ_QUESTION_TIMEOUT", "60"))

DEFAULT_LANG = "uz_lat"
LANG_LABELS = {
    "uz_lat": "🇺🇿 O'zbek (lotin)",
    "uz_cyr": "🇺🇿 Ўзбек (кирил)",
    "ru": "🇷🇺 Русский",
}

PRO_PLANS = {
    "weekly": {
        "title": "Haftalik obuna",
        "price": "15,000",
        "desc": "Tezkor tayyorgarlik uchun",
        "badge": "",
    },
    "monthly": {
        "title": "Oylik obuna",
        "price": "33,000",
        "desc": "Eng optimal tanlov",
        "badge": "⭐ ENG MASHHUR",
    },
    "quarterly": {
        "title": "3 Oylik obuna",
        "price": "83,000",
        "desc": "21% chegirma bilan",
        "badge": "💎",
    },
}
