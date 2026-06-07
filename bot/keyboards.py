from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)

from bot.config import LANG_LABELS


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
                KeyboardButton(text="🌐 Til"),
                KeyboardButton(text="⚙️ Sozlamalar"),
            ],
        ],
        resize_keyboard=True,
    )


def quiz_control_kb(show_next: bool = True) -> InlineKeyboardMarkup:
    buttons = []
    if show_next:
        buttons.append(
            [InlineKeyboardButton(text="➡️ Keyingi savol", callback_data="quiz:next")]
        )
    buttons.append(
        [InlineKeyboardButton(text="🛑 Testni tugatish", callback_data="quiz:stop")]
    )
    return InlineKeyboardMarkup(inline_keyboard=buttons)


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
