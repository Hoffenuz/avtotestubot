from datetime import datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from bot.config import DAILY_QUIZ_HOUR, DAILY_QUIZ_MINUTE


def setup_scheduler(bot) -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler()

    async def daily_job():
        from bot.services.quiz import send_daily_questions

        today = datetime.now().strftime("%Y-%m-%d")
        await send_daily_questions(bot, today)

    scheduler.add_job(
        daily_job,
        CronTrigger(hour=DAILY_QUIZ_HOUR, minute=DAILY_QUIZ_MINUTE),
        id="daily_questions",
        replace_existing=True,
    )
    return scheduler
