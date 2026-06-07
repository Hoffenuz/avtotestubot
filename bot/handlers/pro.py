from aiogram import F, Router
from aiogram.enums import ChatType
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from bot.config import PRO_CONTACT, PRO_PLANS, WEBAPP_URL
from bot.keyboards import pro_main_kb, pro_plans_kb

router = Router()
PRIVATE = F.chat.type == ChatType.PRIVATE


def build_pro_text() -> str:
    plans_lines = []
    for plan_id, plan in PRO_PLANS.items():
        badge = f"<b>{plan['badge']}</b> " if plan["badge"] else ""
        plans_lines.append(
            f"  {badge}<b>{plan['title']}</b>\n"
            f"  💰 <b>{plan['price']}</b> so'm — <i>{plan['desc']}</i>"
        )
    plans_block = "\n\n".join(plans_lines)

    return (
        "━━━━━━━━━━━━━━━━━━━━\n"
        "✦ <b>PRO VERSIYA</b> ✦\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "🚀 <b>Yaxshiroq bazadagi testlar</b>\n"
        "1200+ savol va imtihonbop testlar bilan\n"
        "samarali tayyorlaning.\n\n"
        "🌐 <b>Sayt orqali</b> PRO obuna olish va\n"
        "barcha imkoniyatlardan foydalanish mumkin.\n"
        "Quyidagi <b>🔐 Kirish</b> tugmasi Web App ochadi.\n\n"
        "┈┈┈┈┈┈┈ <b>VS</b> ┈┈┈┈┈┈┈\n\n"
        "📋 <b>Oddiy Versiya</b>\n"
        "  ✅ 700 ta umumiy savollar\n"
        "  ❌ Maxsus videodarsliklar\n"
        "  ❌ Imtihonbop yopiq testlar\n"
        "  ❌ Premium guruh va yordam\n"
        "  ❌ Cheksiz urinishlar va vaqt\n\n"
        "💎 <b>PRO Versiya</b>\n"
        "  ✅ 1200+ ta yopiq savollar bazasi\n"
        "  ✅ To'liq maxsus videodarsliklar\n"
        "  ✅ Imtihonda tushish ehtimoli yuqori testlar\n"
        "  ✅ Admin ko'magi va Premium guruh\n"
        "  ✅ Cheksiz vaqt va urinishlar\n\n"
        "┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈\n"
        "📦 <b>Ta'rifni tanlang</b>\n\n"
        f"{plans_block}\n\n"
        f"📩 Obuna uchun: <b>{PRO_CONTACT}</b>\n"
        f"🔗 Sayt: <a href=\"{WEBAPP_URL}\">avtotestu.uz</a>\n\n"
        "<i>Xarid bo'yicha savollaringiz bo'lsa Telegram orqali yozing.</i>"
    )


def build_plans_text() -> str:
    lines = ["📦 <b>PRO ta'riflar</b>\n"]
    for plan in PRO_PLANS.values():
        badge = f"{plan['badge']}\n" if plan["badge"] else ""
        lines.append(
            f"{badge}"
            f"<b>{plan['title']}</b>\n"
            f"💰 {plan['price']} so'm\n"
            f"📌 {plan['desc']}\n"
        )
    lines.append(
        f"\n🔐 Obuna olish uchun pastdagi tugmani bosing — "
        f"<b>Web App</b> (sayt) ochiladi.\n"
        f"Yoki {PRO_CONTACT} ga yozing."
    )
    return "\n".join(lines)


@router.message(PRIVATE, F.text == "✦ PRO Obuna")
@router.message(PRIVATE, Command("pro"))
async def show_pro(message: Message) -> None:
    await message.answer(
        build_pro_text(),
        parse_mode="HTML",
        disable_web_page_preview=True,
        reply_markup=pro_main_kb(),
    )


@router.callback_query(F.data == "pro:show")
async def pro_show_callback(callback: CallbackQuery) -> None:
    if not callback.message:
        return
    await callback.message.edit_text(
        build_pro_text(),
        parse_mode="HTML",
        disable_web_page_preview=True,
        reply_markup=pro_main_kb(),
    )
    await callback.answer()


@router.callback_query(F.data == "pro:plans")
async def pro_plans_callback(callback: CallbackQuery) -> None:
    if not callback.message:
        return
    await callback.message.edit_text(
        build_plans_text(),
        parse_mode="HTML",
        reply_markup=pro_plans_kb(),
    )
    await callback.answer()


@router.callback_query(F.data == "pro:back")
async def pro_back_callback(callback: CallbackQuery) -> None:
    if not callback.message:
        return
    await callback.message.edit_text(
        build_pro_text(),
        parse_mode="HTML",
        disable_web_page_preview=True,
        reply_markup=pro_main_kb(),
    )
    await callback.answer()
