from aiogram import F, Router
from aiogram.enums import ChatType
from aiogram.types import Message

from bot.database import get_user_stats

router = Router()
PRIVATE = F.chat.type == ChatType.PRIVATE


@router.message(PRIVATE, F.text == "📊 Statistika")
async def show_stats(message: Message) -> None:
    if not message.from_user:
        return

    stats = await get_user_stats(message.from_user.id)

    recent_lines = []
    type_labels = {
        "exam": "🎯 Imtihon",
        "quick": "📝 Tez test",
        "ticket": "📚 Bilet",
        "daily": "☀️ Kunlik",
    }
    for r in stats["recent_results"][:5]:
        label = type_labels.get(r["quiz_type"], r["quiz_type"])
        pct = round(r["correct"] / r["total"] * 100, 1) if r["total"] else 0
        recent_lines.append(f"  • {label}: {r['correct']}/{r['total']} ({pct}%)")

    recent_text = "\n".join(recent_lines) if recent_lines else "  Hali natijalar yo'q"

    await message.answer(
        f"📊 <b>Sizning statistikangiz</b>\n\n"
        f"📝 Jami javoblar: <b>{stats['total_answered']}</b>\n"
        f"✅ To'g'ri javoblar: <b>{stats['total_correct']}</b>\n"
        f"📈 Aniqlik: <b>{stats['accuracy']}%</b>\n"
        f"🎯 Testlar soni: <b>{stats['quiz_count']}</b>\n\n"
        f"<b>Oxirgi natijalar:</b>\n{recent_text}",
        parse_mode="HTML",
    )
