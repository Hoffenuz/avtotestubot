import aiosqlite

from bot.config import DB_PATH


async def init_db() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    async with aiosqlite.connect(DB_PATH) as db:
        await db.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                full_name TEXT,
                language TEXT DEFAULT 'uz_lat',
                daily_enabled INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS quiz_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                quiz_type TEXT NOT NULL,
                total INTEGER NOT NULL,
                correct INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            );

            CREATE TABLE IF NOT EXISTS answer_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                question_id TEXT NOT NULL,
                is_correct INTEGER NOT NULL,
                answered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            );

            CREATE TABLE IF NOT EXISTS daily_sent (
                user_id INTEGER NOT NULL,
                sent_date TEXT NOT NULL,
                PRIMARY KEY (user_id, sent_date)
            );
            """
        )
        await db.commit()


async def upsert_user(user_id: int, username: str | None, full_name: str) -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """
            INSERT INTO users (user_id, username, full_name)
            VALUES (?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                username = excluded.username,
                full_name = excluded.full_name
            """,
            (user_id, username, full_name),
        )
        await db.commit()


async def get_user(user_id: int) -> dict | None:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)) as cur:
            row = await cur.fetchone()
            return dict(row) if row else None


async def set_language(user_id: int, language: str) -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE users SET language = ? WHERE user_id = ?",
            (language, user_id),
        )
        await db.commit()


async def set_daily_enabled(user_id: int, enabled: bool) -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE users SET daily_enabled = ? WHERE user_id = ?",
            (1 if enabled else 0, user_id),
        )
        await db.commit()


async def get_daily_subscribers() -> list[int]:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT user_id FROM users WHERE daily_enabled = 1"
        ) as cur:
            rows = await cur.fetchall()
            return [row[0] for row in rows]


async def mark_daily_sent(user_id: int, sent_date: str) -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT OR IGNORE INTO daily_sent (user_id, sent_date) VALUES (?, ?)",
            (user_id, sent_date),
        )
        await db.commit()


async def was_daily_sent(user_id: int, sent_date: str) -> bool:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT 1 FROM daily_sent WHERE user_id = ? AND sent_date = ?",
            (user_id, sent_date),
        ) as cur:
            return await cur.fetchone() is not None


async def log_answer(user_id: int, question_id: str, is_correct: bool) -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO answer_log (user_id, question_id, is_correct) VALUES (?, ?, ?)",
            (user_id, question_id, 1 if is_correct else 0),
        )
        await db.commit()


async def save_quiz_result(
    user_id: int, quiz_type: str, total: int, correct: int
) -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """
            INSERT INTO quiz_results (user_id, quiz_type, total, correct)
            VALUES (?, ?, ?, ?)
            """,
            (user_id, quiz_type, total, correct),
        )
        await db.commit()


async def get_user_stats(user_id: int) -> dict:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row

        async with db.execute(
            """
            SELECT COUNT(*) as total_answered,
                   SUM(is_correct) as total_correct
            FROM answer_log WHERE user_id = ?
            """,
            (user_id,),
        ) as cur:
            answers = dict(await cur.fetchone())

        async with db.execute(
            """
            SELECT quiz_type, total, correct, created_at
            FROM quiz_results WHERE user_id = ?
            ORDER BY created_at DESC LIMIT 10
            """,
            (user_id,),
        ) as cur:
            recent = [dict(row) for row in await cur.fetchall()]

        async with db.execute(
            "SELECT COUNT(*) FROM quiz_results WHERE user_id = ?",
            (user_id,),
        ) as cur:
            quiz_count = (await cur.fetchone())[0]

    total_answered = answers["total_answered"] or 0
    total_correct = answers["total_correct"] or 0
    accuracy = round(total_correct / total_answered * 100, 1) if total_answered else 0

    return {
        "total_answered": total_answered,
        "total_correct": total_correct,
        "accuracy": accuracy,
        "quiz_count": quiz_count,
        "recent_results": recent,
    }
