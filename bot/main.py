import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.types import PollAnswer

from bot.config import BOT_TOKEN
from bot.database import init_db
from bot.handlers import quiz, start, stats
from bot.services.quiz import handle_poll_answer
from bot.services.scheduler import setup_scheduler

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


async def main() -> None:
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN .env faylida topilmadi!")
        sys.exit(1)

    await init_db()

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    dp.include_router(start.router)
    dp.include_router(quiz.router)
    dp.include_router(stats.router)

    @dp.poll_answer()
    async def on_poll_answer(poll_answer: PollAnswer) -> None:
        await handle_poll_answer(bot, poll_answer)

    scheduler = setup_scheduler(bot)
    scheduler.start()
    logger.info("Kunlik savollar rejalashtirildi")

    logger.info("Bot ishga tushmoqda...")
    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        scheduler.shutdown()
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
