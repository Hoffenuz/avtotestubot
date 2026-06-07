from aiogram import F, Router
from aiogram.enums import ChatType
from aiogram.filters import Command, CommandStart
from aiogram.types import CallbackQuery, Message

from bot.database import set_language, upsert_user
from bot.keyboards import language_kb, main_menu_kb

router = Router()
GROUP = F.chat.type.in_({ChatType.GROUP, ChatType.SUPERGROUP})
PRIVATE = F.chat.type == ChatType.PRIVATE


@router.message(PRIVATE, CommandStart())
async def cmd_start_private(message: Message) -> None:
    user = message.from_user
    if not user:
        return

    await upsert_user(user.id, user.username, user.full_name or "")

    await message.answer(
        f"👋 Salom, <b>{user.full_name}</b>!\n\n"
        "🚗 <b>Avtotest botiga xush kelibsiz!</b>\n\n"
        "Bu bot orqali:\n"
        "• ☀️ Kunlik savollar olasiz\n"
        "• 📝 Tez test va 🎯 imtihon ishlaysiz\n"
        "• 📚 Bilet bo'yicha mashq qilasiz\n"
        "• 👥 Guruhda ham test ishlashingiz mumkin\n"
        "• ✦ PRO obuna — 1200+ savol va maxsus imkoniyatlar\n\n"
        "🔐 <b>Kirish</b> tugmasi orqali sayt (Web App) ochiladi.\n\n"
        "Quyidagi tugmalardan foydalaning 👇",
        parse_mode="HTML",
        reply_markup=main_menu_kb(),
    )


@router.message(GROUP, CommandStart())
async def cmd_start_group(message: Message) -> None:
    await message.answer(
        "🚗 <b>Avtotest bot — guruh rejimi</b>\n\n"
        "👥 <b>Guruh buyruqlari:</b>\n"
        "/test — tez test (10 savol)\n"
        "/imtihon — imtihon (20 savol)\n"
        "/natija — joriy natijalar\n"
        "/stop — testni to'xtatish\n\n"
        "📱 Shaxsiy test uchun botga DM da /start yuboring.",
        parse_mode="HTML",
    )


@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    if message.chat.type == ChatType.PRIVATE:
        text = (
            "<b>📖 Yordam</b>\n\n"
            "<b>📝 Tez test</b> — 10 ta tasodifiy savol\n"
            "<b>🎯 Imtihon</b> — 20 ta savol (86% o'tish balli)\n"
            "<b>📚 Bilet bo'yicha</b> — bilet raqami tanlab mashq\n"
            "<b>📊 Statistika</b> — natijalaringiz\n"
            "<b>🌐 Til</b> — o'zbek (lotin/kiril) yoki rus\n"
            "<b>⚙️ Sozlamalar</b> — kunlik savollar\n"
            "<b>✦ PRO Obuna</b> — premium imkoniyatlar\n"
            "<b>🔐 Kirish</b> — sayt orqali (Web App)\n\n"
            "/start — bosh menyu\n"
            "/stop — testni to'xtatish\n"
            "/help — yordam"
        )
    else:
        text = (
            "<b>📖 Guruh yordami</b>\n\n"
            "/test — guruh tez testi\n"
            "/imtihon — guruh imtihoni\n"
            "/natija — natijalar jadvali\n"
            "/stop — testni to'xtatish\n"
            "/help — yordam"
        )
    await message.answer(text, parse_mode="HTML")


@router.message(PRIVATE, F.text == "🌐 Til")
async def show_language(message: Message) -> None:
    await message.answer("🌐 Tilni tanlang:", reply_markup=language_kb())


@router.callback_query(F.data.startswith("lang:"))
async def set_lang_callback(callback: CallbackQuery) -> None:
    if not callback.from_user or not callback.data:
        return

    lang = callback.data.split(":")[1]
    await set_language(callback.from_user.id, lang)
    await callback.answer("Til o'zgartirildi!")
    if callback.message:
        await callback.message.edit_text("✅ Til muvaffaqiyatli o'zgartirildi!")
