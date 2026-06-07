from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import CallbackQuery, Message

from bot.database import set_language, upsert_user
from bot.keyboards import language_kb, main_menu_kb

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
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
        "• 🖼 Rasmli savollar quiz ko'rinishida\n\n"
        "Quyidagi tugmalardan foydalaning 👇",
        parse_mode="HTML",
        reply_markup=main_menu_kb(),
    )


@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    await message.answer(
        "<b>📖 Yordam</b>\n\n"
        "<b>📝 Tez test</b> — 10 ta tasodifiy savol\n"
        "<b>🎯 Imtihon</b> — 20 ta savol (86% o'tish balli)\n"
        "<b>📚 Bilet bo'yicha</b> — bilet raqami tanlab mashq\n"
        "<b>📊 Statistika</b> — natijalaringiz\n"
        "<b>🌐 Til</b> — o'zbek (lotin/kiril) yoki rus\n"
        "<b>⚙️ Sozlamalar</b> — kunlik savollar yoqish/o'chirish\n\n"
        "/start — bosh menyu\n"
        "/help — yordam",
        parse_mode="HTML",
    )


@router.message(F.text == "🌐 Til")
async def show_language(message: Message) -> None:
    await message.answer(
        "🌐 Tilni tanlang:",
        reply_markup=language_kb(),
    )


@router.callback_query(F.data.startswith("lang:"))
async def set_lang_callback(callback: CallbackQuery) -> None:
    if not callback.from_user or not callback.data:
        return

    lang = callback.data.split(":")[1]
    await set_language(callback.from_user.id, lang)
    await callback.answer("Til o'zgartirildi!")
    if callback.message:
        await callback.message.edit_text("✅ Til muvaffaqiyatli o'zgartirildi!")
