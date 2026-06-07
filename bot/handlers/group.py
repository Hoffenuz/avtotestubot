from aiogram import F, Router
from aiogram.enums import ChatType
from aiogram.filters import Command
from aiogram.types import Message

from bot.database import get_user, upsert_user
from bot.services.quiz import send_group_quiz_poll
from bot.services.quiz_session import (
    end_group_session,
    get_group_session,
    start_group_session,
)

router = Router()
GROUP = F.chat.type.in_({ChatType.GROUP, ChatType.SUPERGROUP})


async def _get_lang(user_id: int) -> str:
    user = await get_user(user_id)
    return user["language"] if user else "uz_lat"


@router.message(GROUP, Command("test"))
async def group_quick_test(message: Message) -> None:
    if not message.from_user:
        return

    await upsert_user(
        message.from_user.id,
        message.from_user.username,
        message.from_user.full_name or "",
    )
    lang = await _get_lang(message.from_user.id)
    session = start_group_session(message.chat.id, message.from_user.id, "group_quick", lang)

    await message.answer(
        f"👥 <b>Guruh tez testi boshlandi!</b>\n"
        f"📝 {len(session.questions)} ta savol — har biri <b>1 daqiqa</b>\n"
        f"Boshlagan: {message.from_user.full_name}\n\n"
        "Hammangiz javob bering!",
        parse_mode="HTML",
    )
    await send_group_quiz_poll(message.bot, session)


@router.message(GROUP, Command("imtihon"))
async def group_exam(message: Message) -> None:
    if not message.from_user:
        return

    await upsert_user(
        message.from_user.id,
        message.from_user.username,
        message.from_user.full_name or "",
    )
    lang = await _get_lang(message.from_user.id)
    session = start_group_session(message.chat.id, message.from_user.id, "group_exam", lang)

    await message.answer(
        f"👥 <b>Guruh imtihoni boshlandi!</b>\n"
        f"🎯 {len(session.questions)} ta savol — har biri <b>1 daqiqa</b>\n"
        f"Boshlagan: {message.from_user.full_name}\n\n"
        "Hammangiz javob bering!",
        parse_mode="HTML",
    )
    await send_group_quiz_poll(message.bot, session)


@router.message(GROUP, Command("natija"))
async def group_scores(message: Message) -> None:
    session = get_group_session(message.chat.id)
    if not session or not session.scores:
        await message.answer("📊 Hali natijalar yo'q yoki test boshlanmagan.")
        return

    from bot.services.quiz import format_group_leaderboard

    total = len(session.questions)
    await message.answer(
        f"📊 <b>Joriy natijalar</b> (savol {session.progress_text}):\n\n"
        f"{format_group_leaderboard(session)}",
        parse_mode="HTML",
    )


@router.message(GROUP, Command("stop"))
async def group_stop(message: Message) -> None:
    session = end_group_session(message.chat.id)
    if session:
        await message.answer(
            f"🛑 Guruh testi to'xtatildi.\n"
            f"Savol: {session.current_index}/{len(session.questions)}"
        )
    else:
        await message.answer("Faol guruh testi yo'q.")
