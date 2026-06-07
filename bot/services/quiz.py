import asyncio
import logging

from aiogram import Bot
from aiogram.types import PollAnswer

from bot.config import DAILY_QUESTIONS_COUNT, QUIZ_QUESTION_TIMEOUT
from bot.database import (
    get_daily_subscribers,
    get_user,
    log_answer,
    mark_daily_sent,
    save_quiz_result,
    was_daily_sent,
)
from bot.keyboards import exam_result_kb
from bot.services.quiz_session import (
    GroupQuizSession,
    QuizSession,
    cancel_group_timer,
    cancel_private_timer,
    end_group_session,
    end_session,
    get_group_session,
    get_session,
    register_poll,
    resolve_poll,
    set_timer,
    start_group_session,
    start_session,
    unregister_poll,
    _timer_key_group,
    _timer_key_private,
)

logger = logging.getLogger(__name__)

_answer_locks: dict[int, asyncio.Lock] = {}
_group_locks: dict[int, asyncio.Lock] = {}
POLL_QUESTION_MAX = 300
POLL_OPTION_MAX = 100


def _get_lock(user_id: int) -> asyncio.Lock:
    if user_id not in _answer_locks:
        _answer_locks[user_id] = asyncio.Lock()
    return _answer_locks[user_id]


def _get_group_lock(chat_id: int) -> asyncio.Lock:
    if chat_id not in _group_locks:
        _group_locks[chat_id] = asyncio.Lock()
    return _group_locks[chat_id]


def _build_header(session: QuizSession | GroupQuizSession, question) -> str:
    if session.quiz_type == "exam":
        return f"🎯 Imtihon — savol {session.progress_text}"
    if session.quiz_type == "quick":
        return f"📝 Tez test — savol {session.progress_text}"
    if session.quiz_type == "ticket":
        return f"📚 Bilet #{question.ticket_num} — savol {session.progress_text}"
    if session.quiz_type == "daily":
        return f"☀️ Kunlik savol {session.progress_text}"
    if session.quiz_type == "group_exam":
        return f"👥 Guruh imtihoni — savol {session.progress_text}"
    if session.quiz_type == "group_quick":
        return f"👥 Guruh testi — savol {session.progress_text}"
    return f"Savol {session.progress_text}"


def _prepare_poll_text(question_text: str) -> str:
    text = question_text.strip()
    if len(text) > POLL_QUESTION_MAX:
        return text[: POLL_QUESTION_MAX - 3] + "..."
    return text


def _prepare_options(options: list[str]) -> list[str]:
    return [opt[:POLL_OPTION_MAX] for opt in options[:10]]


def _poll_question(header: str, question_text: str) -> str:
    """Savol matni faqat poll ichida — header alohida xabar."""
    return _prepare_poll_text(question_text)


async def _send_poll(
    bot: Bot,
    chat_id: int,
    header: str,
    question,
    mode: str,
    entity_id: int,
) -> str | None:
    poll_q = _poll_question(header, question.text)
    options = _prepare_options(question.options)

    await bot.send_message(chat_id=chat_id, text=header)

    if question.image_url:
        try:
            await bot.send_photo(chat_id=chat_id, photo=question.image_url)
            await asyncio.sleep(0.4)
        except Exception:
            logger.warning("Rasm yuborilmadi: %s", question.image_url, exc_info=True)

    try:
        msg = await bot.send_poll(
            chat_id=chat_id,
            question=poll_q,
            options=options,
            type="quiz",
            correct_option_id=question.correct_index,
            is_anonymous=False,
            open_period=QUIZ_QUESTION_TIMEOUT,
        )
    except Exception:
        logger.error("Poll yuborilmadi: %s", question.global_id, exc_info=True)
        try:
            msg = await bot.send_poll(
                chat_id=chat_id,
                question=_prepare_poll_text(question.text),
                options=options,
                type="quiz",
                correct_option_id=question.correct_index,
                is_anonymous=False,
                open_period=QUIZ_QUESTION_TIMEOUT,
            )
        except Exception:
            logger.error("Poll yuborib bo'lmadi: %s", question.global_id, exc_info=True)
            return None

    register_poll(msg.poll.id, mode, entity_id)
    return msg.poll.id


async def send_quiz_poll(bot: Bot, chat_id: int, session: QuizSession) -> None:
    question = session.current
    if not question:
        return

    cancel_private_timer(session.user_id)
    unregister_poll(session.current_poll_id)
    session.waiting_answer = False
    session.current_poll_id = None

    header = _build_header(session, question)
    poll_id = await _send_poll(bot, chat_id, header, question, "private", session.user_id)

    if not poll_id:
        await bot.send_message(chat_id=chat_id, text="⚠️ Savol yuborilmadi. Keyingi savol...")
        session.current_index += 1
        if session.is_finished:
            await finish_quiz(bot, chat_id, session)
        else:
            await send_quiz_poll(bot, chat_id, session)
        return

    session.current_poll_id = poll_id
    session.waiting_answer = True
    set_timer(
        _timer_key_private(session.user_id),
        asyncio.create_task(_private_timeout(bot, session.user_id, poll_id)),
    )


async def send_group_quiz_poll(bot: Bot, session: GroupQuizSession) -> None:
    question = session.current
    if not question:
        return

    cancel_group_timer(session.chat_id)
    unregister_poll(session.current_poll_id)
    session.waiting_answer = False
    session.current_poll_id = None
    session.answered.clear()

    header = _build_header(session, question)
    poll_id = await _send_poll(
        bot, session.chat_id, header, question, "group", session.chat_id
    )

    if not poll_id:
        session.current_index += 1
        if session.is_finished:
            await finish_group_quiz(bot, session)
        else:
            await send_group_quiz_poll(bot, session)
        return

    session.current_poll_id = poll_id
    session.waiting_answer = True
    set_timer(
        _timer_key_group(session.chat_id),
        asyncio.create_task(_group_timeout(bot, session.chat_id, poll_id)),
    )


async def _private_timeout(bot: Bot, user_id: int, poll_id: str) -> None:
    try:
        await asyncio.sleep(QUIZ_QUESTION_TIMEOUT)
        async with _get_lock(user_id):
            session = get_session(user_id)
            if not session or not session.waiting_answer:
                return
            if session.current_poll_id != poll_id:
                return

            session.waiting_answer = False
            unregister_poll(session.current_poll_id)
            session.current_poll_id = None

            question = session.current
            if question:
                await log_answer(user_id, question.global_id, False)

            session.current_index += 1

            if session.is_finished:
                await finish_quiz(bot, session.chat_id, session)
            else:
                await bot.send_message(chat_id=session.chat_id, text="⏱ Vaqt tugadi!")
                await send_quiz_poll(bot, session.chat_id, session)
    except asyncio.CancelledError:
        pass


async def _group_timeout(bot: Bot, chat_id: int, poll_id: str) -> None:
    try:
        await asyncio.sleep(QUIZ_QUESTION_TIMEOUT)
        async with _get_group_lock(chat_id):
            session = get_group_session(chat_id)
            if not session or not session.waiting_answer:
                return
            if session.current_poll_id != poll_id:
                return

            session.waiting_answer = False
            unregister_poll(session.current_poll_id)
            session.current_poll_id = None
            session.answered.clear()
            session.current_index += 1

            if session.is_finished:
                await finish_group_quiz(bot, session)
            else:
                await bot.send_message(chat_id=chat_id, text="⏱ Vaqt tugadi! Keyingi savol...")
                await send_group_quiz_poll(bot, session)
    except asyncio.CancelledError:
        pass


async def _advance_after_answer(
    bot: Bot, session: QuizSession, is_correct: bool
) -> None:
    unregister_poll(session.current_poll_id)
    session.current_poll_id = None

    if session.is_finished:
        await finish_quiz(bot, session.chat_id, session)
    else:
        result_text = "✅ To'g'ri!" if is_correct else "❌ Noto'g'ri."
        await bot.send_message(chat_id=session.chat_id, text=result_text)
        await asyncio.sleep(0.3)
        await send_quiz_poll(bot, session.chat_id, session)


async def finish_quiz(bot: Bot, chat_id: int, session: QuizSession) -> None:
    cancel_private_timer(session.user_id)
    session.waiting_answer = False
    unregister_poll(session.current_poll_id)
    session.current_poll_id = None

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

    await bot.send_message(
        chat_id=chat_id,
        text=text,
        parse_mode="HTML",
        reply_markup=exam_result_kb() if session.quiz_type == "exam" else None,
    )
    end_session(session.user_id)


def format_group_leaderboard(session: GroupQuizSession) -> str:
    total = len(session.questions)
    if not session.scores:
        return "Hali natijalar yo'q."

    ranked = sorted(session.scores.items(), key=lambda x: (-x[1], x[0]))
    lines = []
    for i, (uid, score) in enumerate(ranked[:15], 1):
        name = session.names.get(uid, f"User {uid}")
        pct = round(score / total * 100, 1) if total else 0
        medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
        lines.append(f"{medal} <b>{name}</b> — {score}/{total} ({pct}%)")
    return "\n".join(lines)


async def finish_group_quiz(bot: Bot, session: GroupQuizSession) -> None:
    cancel_group_timer(session.chat_id)
    session.waiting_answer = False
    unregister_poll(session.current_poll_id)

    total = len(session.questions)
    label = "Guruh imtihoni" if session.quiz_type == "group_exam" else "Guruh testi"

    text = (
        f"🏁 <b>{label} yakunlandi!</b>\n\n"
        f"📊 <b>Natijalar:</b>\n{format_group_leaderboard(session)}"
    )
    await bot.send_message(chat_id=session.chat_id, text=text, parse_mode="HTML")
    end_group_session(session.chat_id)


async def handle_poll_answer(bot: Bot, poll_answer: PollAnswer) -> None:
    user = poll_answer.user
    if not user:
        return

    resolved = resolve_poll(poll_answer.poll_id)
    if not resolved:
        return

    mode, entity_id = resolved
    if mode == "private":
        await _handle_private_poll_answer(bot, poll_answer, entity_id)
    elif mode == "group":
        await _handle_group_poll_answer(bot, poll_answer, entity_id)


async def _handle_private_poll_answer(
    bot: Bot, poll_answer: PollAnswer, user_id: int
) -> None:
    async with _get_lock(user_id):
        session = get_session(user_id)
        if not session or session.is_finished or not session.waiting_answer:
            return
        if session.current_poll_id != poll_answer.poll_id:
            return

        cancel_private_timer(user_id)
        session.waiting_answer = False

        question = session.current
        if not question:
            return

        selected = poll_answer.option_ids[0] if poll_answer.option_ids else -1
        is_correct = selected == question.correct_index
        if is_correct:
            session.correct_count += 1

        await log_answer(user_id, question.global_id, is_correct)
        session.current_index += 1

        await _advance_after_answer(bot, session, is_correct)


async def _handle_group_poll_answer(
    bot: Bot, poll_answer: PollAnswer, chat_id: int
) -> None:
    user = poll_answer.user
    if not user:
        return

    async with _get_group_lock(chat_id):
        session = get_group_session(chat_id)
        if not session or session.is_finished or not session.waiting_answer:
            return
        if session.current_poll_id != poll_answer.poll_id:
            return
        if user.id in session.answered:
            return

        session.answered.add(user.id)
        session.names[user.id] = user.full_name or user.username or str(user.id)

        question = session.current
        if not question:
            return

        selected = poll_answer.option_ids[0] if poll_answer.option_ids else -1
        is_correct = selected == question.correct_index

        if is_correct:
            session.scores[user.id] = session.scores.get(user.id, 0) + 1

        await log_answer(user.id, question.global_id, is_correct)


async def send_daily_questions(bot: Bot, date_str: str) -> None:
    subscribers = await get_daily_subscribers()
    for user_id in subscribers:
        if await was_daily_sent(user_id, date_str):
            continue

        user = await get_user(user_id)
        lang = user["language"] if user else "uz_lat"

        session = start_session(user_id, user_id, "daily", lang)
        if not session.questions:
            continue

        await bot.send_message(
            chat_id=user_id,
            text=(
                f"☀️ <b>Kunlik {DAILY_QUESTIONS_COUNT} ta savol!</b>\n"
                "Har bir savolga 1 daqiqa vaqt beriladi."
            ),
            parse_mode="HTML",
        )
        await send_quiz_poll(bot, user_id, session)
        await mark_daily_sent(user_id, date_str)
