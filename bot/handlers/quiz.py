from aiogram import F, Router
from aiogram.enums import ChatType
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from bot.database import get_user, set_daily_enabled
from bot.keyboards import settings_kb, tickets_kb
from bot.services.quiz import send_quiz_poll
from bot.services.quiz_session import end_session, start_session

router = Router()
PRIVATE = F.chat.type == ChatType.PRIVATE


async def _get_lang(user_id: int) -> str:
    user = await get_user(user_id)
    return user["language"] if user else "uz_lat"


@router.message(PRIVATE, F.text == "📝 Tez test")
async def start_quick_quiz(message: Message) -> None:
    if not message.from_user:
        return

    user_id = message.from_user.id
    lang = await _get_lang(user_id)
    session = start_session(user_id, message.chat.id, "quick", lang)
    await message.answer(
        f"📝 <b>Tez test boshlandi!</b>\n"
        f"Savollar soni: {len(session.questions)}\n"
        f"Har bir savol: <b>1 daqiqa</b>",
        parse_mode="HTML",
    )
    await send_quiz_poll(message.bot, message.chat.id, session)


@router.message(PRIVATE, F.text == "🎯 Imtihon")
async def start_exam(message: Message) -> None:
    if not message.from_user:
        return

    user_id = message.from_user.id
    lang = await _get_lang(user_id)
    session = start_session(user_id, message.chat.id, "exam", lang)
    await message.answer(
        f"🎯 <b>Imtihon boshlandi!</b>\n"
        f"Savollar: {len(session.questions)}\n"
        f"O'tish balli: <b>86%</b>\n"
        f"Har bir savol: <b>1 daqiqa</b>\n\n"
        "Omad!",
        parse_mode="HTML",
    )
    await send_quiz_poll(message.bot, message.chat.id, session)


@router.callback_query(F.data == "quiz:exam")
async def restart_exam(callback: CallbackQuery) -> None:
    if not callback.from_user or not callback.message:
        return

    user_id = callback.from_user.id
    lang = await _get_lang(user_id)
    session = start_session(user_id, callback.message.chat.id, "exam", lang)
    await callback.answer()
    await callback.message.answer("🎯 Yangi imtihon boshlandi!")
    await send_quiz_poll(callback.bot, callback.message.chat.id, session)


@router.message(PRIVATE, F.text == "📚 Bilet bo'yicha")
async def show_tickets(message: Message) -> None:
    await message.answer(
        "📚 Bilet raqamini tanlang:",
        reply_markup=tickets_kb(),
    )


@router.callback_query(F.data.startswith("tickets_page:"))
async def tickets_page(callback: CallbackQuery) -> None:
    if not callback.data or not callback.message:
        return
    page = int(callback.data.split(":")[1])
    await callback.message.edit_reply_markup(reply_markup=tickets_kb(page))
    await callback.answer()


@router.callback_query(F.data.startswith("ticket:"))
async def start_ticket_quiz(callback: CallbackQuery) -> None:
    if not callback.from_user or not callback.data or not callback.message:
        return

    user_id = callback.from_user.id
    ticket_num = int(callback.data.split(":")[1])
    lang = await _get_lang(user_id)
    session = start_session(user_id, callback.message.chat.id, "ticket", lang, ticket_num=ticket_num)

    if not session.questions:
        await callback.answer("Bu biletda savollar topilmadi!", show_alert=True)
        return

    await callback.answer()
    await callback.message.answer(
        f"📚 <b>Bilet #{ticket_num}</b> — {len(session.questions)} ta savol\n"
        f"Har bir savol: <b>1 daqiqa</b>",
        parse_mode="HTML",
    )
    await send_quiz_poll(callback.bot, callback.message.chat.id, session)


@router.callback_query(F.data == "quiz:stop")
async def stop_quiz(callback: CallbackQuery) -> None:
    if not callback.from_user:
        return

    session = end_session(callback.from_user.id)
    await callback.answer("Test to'xtatildi.")
    if callback.message and session:
        await callback.message.answer(
            f"🛑 Test to'xtatildi.\n"
            f"Javob berilgan: {session.current_index}/{len(session.questions)}\n"
            f"To'g'ri: {session.correct_count}"
        )


@router.message(PRIVATE, Command("stop"))
async def stop_quiz_command(message: Message) -> None:
    if not message.from_user:
        return

    session = end_session(message.from_user.id)
    if session:
        await message.answer(
            f"🛑 Test to'xtatildi.\n"
            f"Javob berilgan: {session.current_index}/{len(session.questions)}\n"
            f"To'g'ri: {session.correct_count}"
        )
    else:
        await message.answer("Faol test yo'q.")


@router.message(PRIVATE, F.text == "⚙️ Sozlamalar")
async def show_settings(message: Message) -> None:
    if not message.from_user:
        return

    user = await get_user(message.from_user.id)
    daily = bool(user and user.get("daily_enabled", 1))
    await message.answer(
        "⚙️ <b>Sozlamalar</b>",
        parse_mode="HTML",
        reply_markup=settings_kb(daily),
    )


@router.callback_query(F.data == "settings:daily")
async def toggle_daily(callback: CallbackQuery) -> None:
    if not callback.from_user:
        return

    user = await get_user(callback.from_user.id)
    current = bool(user and user.get("daily_enabled", 1))
    await set_daily_enabled(callback.from_user.id, not current)

    status = "yoqildi" if not current else "o'chirildi"
    await callback.answer(f"Kunlik savollar {status}!")
    if callback.message:
        await callback.message.edit_reply_markup(
            reply_markup=settings_kb(not current)
        )
