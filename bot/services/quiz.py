import logging

from aiogram import Bot
from aiogram.types import PollAnswer

from bot.config import DAILY_QUESTIONS_COUNT
from bot.database import (
    get_daily_subscribers,
    get_user,
    log_answer,
    mark_daily_sent,
    save_quiz_result,
    was_daily_sent,
)
from bot.keyboards import quiz_control_kb
from bot.services.quiz_session import QuizSession, end_session, get_session, start_session

logger = logging.getLogger(__name__)


async def send_quiz_poll(bot: Bot, chat_id: int, session: QuizSession) -> None:
    question = session.current
    if not question:
        return

    if question.image_url:
        try:
            await bot.send_photo(chat_id=chat_id, photo=question.image_url)
        except Exception:
            logger.warning("Rasm yuborilmadi: %s", question.image_url)

    header = ""
    if session.quiz_type == "exam":
        header = f"🎯 Imtihon — savol {session.progress_text}\n\n"
    elif session.quiz_type == "quick":
        header = f"📝 Tez test — savol {session.progress_text}\n\n"
    elif session.quiz_type == "ticket":
        header = f"📚 Bilet #{question.ticket_num} — savol {session.progress_text}\n\n"
    elif session.quiz_type == "daily":
        header = f"☀️ Kunlik savol {session.progress_text}\n\n"

    poll_text = f"{header}{question.text}"
    if len(poll_text) > 300:
        poll_text = poll_text[:297] + "..."

    await bot.send_poll(
        chat_id=chat_id,
        question=poll_text,
        options=question.options[:10],
        type="quiz",
        correct_option_id=question.correct_index,
        is_anonymous=False,
        open_period=120,
    )


async def finish_quiz(bot: Bot, chat_id: int, session: QuizSession) -> None:
    total = len(session.questions)
    correct = session.correct_count
    pct = round(correct / total * 100, 1) if total else 0

    await save_quiz_result(session.user_id, session.quiz_type, total, correct)

    passed = pct >= 86
    emoji = "✅" if passed else "❌"
    type_labels = {
        "exam": "Imtihon",
        "quick": "Tez test",
        "ticket": "Bilet testi",
        "daily": "Kunlik test",
    }
    label = type_labels.get(session.quiz_type, "Test")

    text = (
        f"{emoji} <b>{label} yakunlandi!</b>\n\n"
        f"📊 Natija: <b>{correct}/{total}</b> ({pct}%)\n"
    )
    if session.quiz_type == "exam":
        text += (
            "✅ O'tdingiz!" if passed else "❌ O'ta olmadingiz (kamida 86% kerak)\n"
        )

    from bot.keyboards import exam_result_kb

    await bot.send_message(
        chat_id=chat_id,
        text=text,
        parse_mode="HTML",
        reply_markup=exam_result_kb() if session.quiz_type == "exam" else None,
    )
    end_session(session.user_id)


async def handle_poll_answer(bot: Bot, poll_answer: PollAnswer) -> None:
    user_id = poll_answer.user.id
    session = get_session(user_id)
    if not session or session.is_finished:
        return

    question = session.current
    if not question:
        return

    selected = poll_answer.option_ids[0] if poll_answer.option_ids else -1
    is_correct = selected == question.correct_index
    if is_correct:
        session.correct_count += 1

    await log_answer(user_id, question.global_id, is_correct)

    session.current_index += 1
    session.answered = False

    if session.is_finished:
        await finish_quiz(bot, user_id, session)
    else:
        result_text = "✅ To'g'ri!" if is_correct else "❌ Noto'g'ri."
        await bot.send_message(
            chat_id=user_id,
            text=f"{result_text}\nKeyingi savolga o'tamiz...",
            reply_markup=quiz_control_kb(),
        )


async def send_next_question(bot: Bot, user_id: int) -> bool:
    session = get_session(user_id)
    if not session or session.is_finished:
        return False
    await send_quiz_poll(bot, user_id, session)
    return True


async def send_daily_questions(bot: Bot, date_str: str) -> None:
    subscribers = await get_daily_subscribers()
    for user_id in subscribers:
        if await was_daily_sent(user_id, date_str):
            continue

        user = await get_user(user_id)
        lang = user["language"] if user else "uz_lat"

        session = start_session(user_id, "daily", lang)
        if not session.questions:
            continue

        await bot.send_message(
            chat_id=user_id,
            text=(
                f"☀️ <b>Kunlik {DAILY_QUESTIONS_COUNT} ta savol!</b>\n"
                "Har bir savolga quiz shaklida javob bering."
            ),
            parse_mode="HTML",
        )
        await send_quiz_poll(bot, user_id, session)
        await mark_daily_sent(user_id, date_str)
