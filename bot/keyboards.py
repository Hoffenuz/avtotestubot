from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
    WebAppInfo,
)

from bot.config import LANG_LABELS, PRO_CONTACT, PRO_PLANS, WEBAPP_URL


def main_menu_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="📝 Tez test"),
                KeyboardButton(text="🎯 Imtihon"),
            ],
            [
                KeyboardButton(text="📚 Bilet bo'yicha"),
                KeyboardButton(text="📊 Statistika"),
            ],
            [
                KeyboardButton(text="✦ PRO Obuna"),
                KeyboardButton(
                    text="🔐 Kirish",
                    web_app=WebAppInfo(url=WEBAPP_URL),
                ),
            ],
            [
                KeyboardButton(text="🌐 Til"),
                KeyboardButton(text="⚙️ Sozlamalar"),
            ],
        ],
        resize_keyboard=True,
    )


def pro_main_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🔐 Sayt orqali kirish",
                    web_app=WebAppInfo(url=WEBAPP_URL),
                ),
            ],
            [
                InlineKeyboardButton(
                    text="🎁 Sinab ko'rish",
                    web_app=WebAppInfo(url=f"{WEBAPP_URL}/trial"),
                ),
                InlineKeyboardButton(
                    text="💎 PRO olish",
                    callback_data="pro:plans",
                ),
            ],
            [
                InlineKeyboardButton(
                    text=f"💬 Admin bilan bog'lanish",
                    url=f"https://t.me/{PRO_CONTACT.lstrip('@')}",
                ),
            ],
        ]
    )


def pro_plans_kb() -> InlineKeyboardMarkup:
    rows = []
    for plan_id, plan in PRO_PLANS.items():
        badge = f"{plan['badge']} " if plan["badge"] else ""
        rows.append(
            [
                InlineKeyboardButton(
                    text=f"{badge}{plan['title']} — {plan['price']} so'm",
                    web_app=WebAppInfo(url=f"{WEBAPP_URL}/subscribe/{plan_id}"),
                )
            ]
        )
    rows.append(
        [
            InlineKeyboardButton(
                text="🔐 Kirish (Web App)",
                web_app=WebAppInfo(url=WEBAPP_URL),
            ),
        ]
    )
    rows.append(
        [
            InlineKeyboardButton(
                text=f"📩 {PRO_CONTACT}",
                url=f"https://t.me/{PRO_CONTACT.lstrip('@')}",
            ),
            InlineKeyboardButton(text="⬅️ Orqaga", callback_data="pro:back"),
        ]
    )
    return InlineKeyboardMarkup(inline_keyboard=rows)


def language_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=label, callback_data=f"lang:{code}"
                )
            ]
            for code, label in LANG_LABELS.items()
        ]
    )


def settings_kb(daily_enabled: bool) -> InlineKeyboardMarkup:
    toggle_text = (
        "🔕 Kunlik savollarni o'chirish"
        if daily_enabled
        else "🔔 Kunlik savollarni yoqish"
    )
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=toggle_text, callback_data="settings:daily")],
            [
                InlineKeyboardButton(
                    text="✦ PRO Obuna",
                    callback_data="pro:show",
                ),
            ],
        ]
    )


def tickets_kb(page: int = 0, per_page: int = 10) -> InlineKeyboardMarkup:
    from bot.services.questions import question_bank

    tickets = question_bank.ticket_numbers()
    start = page * per_page
    end = start + per_page
    page_tickets = tickets[start:end]

    rows = [
        [
            InlineKeyboardButton(
                text=f"Bilet #{num}",
                callback_data=f"ticket:{num}",
            )
        ]
        for num in page_tickets
    ]

    nav = []
    if page > 0:
        nav.append(
            InlineKeyboardButton(text="⬅️", callback_data=f"tickets_page:{page - 1}")
        )
    if end < len(tickets):
        nav.append(
            InlineKeyboardButton(text="➡️", callback_data=f"tickets_page:{page + 1}")
        )
    if nav:
        rows.append(nav)

    rows.append(
        [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="quiz:stop")]
    )
    return InlineKeyboardMarkup(inline_keyboard=rows)


def exam_result_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🔄 Qayta ishlash", callback_data="quiz:exam"
                ),
            ]
        ]
    )
