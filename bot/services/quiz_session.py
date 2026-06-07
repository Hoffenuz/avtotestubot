import asyncio
from dataclasses import dataclass, field

from bot.config import EXAM_QUESTIONS_COUNT, QUICK_QUIZ_COUNT
from bot.services.questions import Question, question_bank

_timers: dict[str, asyncio.Task] = {}
_poll_map: dict[str, tuple[str, int]] = {}


@dataclass
class QuizSession:
    user_id: int
    chat_id: int
    quiz_type: str
    questions: list[Question] = field(default_factory=list)
    current_index: int = 0
    correct_count: int = 0
    waiting_answer: bool = False
    current_poll_id: str | None = None
    lang: str = "uz_lat"

    @property
    def current(self) -> Question | None:
        if 0 <= self.current_index < len(self.questions):
            return self.questions[self.current_index]
        return None

    @property
    def is_finished(self) -> bool:
        return self.current_index >= len(self.questions)

    @property
    def progress_text(self) -> str:
        return f"{self.current_index + 1}/{len(self.questions)}"


@dataclass
class GroupQuizSession:
    chat_id: int
    host_id: int
    quiz_type: str
    questions: list[Question] = field(default_factory=list)
    current_index: int = 0
    waiting_answer: bool = False
    current_poll_id: str | None = None
    lang: str = "uz_lat"
    scores: dict[int, int] = field(default_factory=dict)
    answered: set[int] = field(default_factory=set)
    names: dict[int, str] = field(default_factory=dict)

    @property
    def current(self) -> Question | None:
        if 0 <= self.current_index < len(self.questions):
            return self.questions[self.current_index]
        return None

    @property
    def is_finished(self) -> bool:
        return self.current_index >= len(self.questions)

    @property
    def progress_text(self) -> str:
        return f"{self.current_index + 1}/{len(self.questions)}"


_sessions: dict[int, QuizSession] = {}
_group_sessions: dict[int, GroupQuizSession] = {}


def _timer_key_private(user_id: int) -> str:
    return f"u:{user_id}"


def _timer_key_group(chat_id: int) -> str:
    return f"g:{chat_id}"


def register_poll(poll_id: str, mode: str, entity_id: int) -> None:
    _poll_map[poll_id] = (mode, entity_id)


def resolve_poll(poll_id: str) -> tuple[str, int] | None:
    return _poll_map.get(poll_id)


def unregister_poll(poll_id: str | None) -> None:
    if poll_id:
        _poll_map.pop(poll_id, None)


def cancel_timer(key: str) -> None:
    task = _timers.pop(key, None)
    if task and not task.done():
        task.cancel()


def cancel_private_timer(user_id: int) -> None:
    cancel_timer(_timer_key_private(user_id))


def cancel_group_timer(chat_id: int) -> None:
    cancel_timer(_timer_key_group(chat_id))


def set_timer(key: str, task: asyncio.Task) -> None:
    cancel_timer(key)
    _timers[key] = task


def get_session(user_id: int) -> QuizSession | None:
    return _sessions.get(user_id)


def get_group_session(chat_id: int) -> GroupQuizSession | None:
    return _group_sessions.get(chat_id)


def _load_questions(
    quiz_type: str, lang: str, ticket_num: int | None = None
) -> list[Question]:
    if quiz_type == "exam":
        return question_bank.get_random(EXAM_QUESTIONS_COUNT, lang)
    if quiz_type == "quick":
        return question_bank.get_random(QUICK_QUIZ_COUNT, lang)
    if quiz_type == "ticket" and ticket_num is not None:
        return question_bank.get_by_ticket(ticket_num, lang)
    if quiz_type == "daily":
        from bot.config import DAILY_QUESTIONS_COUNT

        return question_bank.get_daily_questions(DAILY_QUESTIONS_COUNT, lang)
    return question_bank.get_random(QUICK_QUIZ_COUNT, lang)


def start_session(
    user_id: int,
    chat_id: int,
    quiz_type: str,
    lang: str = "uz_lat",
    ticket_num: int | None = None,
) -> QuizSession:
    cancel_private_timer(user_id)
    old = _sessions.pop(user_id, None)
    if old and old.current_poll_id:
        unregister_poll(old.current_poll_id)

    session = QuizSession(
        user_id=user_id,
        chat_id=chat_id,
        quiz_type=quiz_type,
        questions=_load_questions(quiz_type, lang, ticket_num),
        lang=lang,
    )
    _sessions[user_id] = session
    return session


def start_group_session(
    chat_id: int,
    host_id: int,
    quiz_type: str,
    lang: str = "uz_lat",
) -> GroupQuizSession:
    cancel_group_timer(chat_id)
    old = _group_sessions.pop(chat_id, None)
    if old and old.current_poll_id:
        unregister_poll(old.current_poll_id)

    session = GroupQuizSession(
        chat_id=chat_id,
        host_id=host_id,
        quiz_type=quiz_type,
        questions=_load_questions(quiz_type, lang),
        lang=lang,
    )
    _group_sessions[chat_id] = session
    return session


def end_session(user_id: int) -> QuizSession | None:
    cancel_private_timer(user_id)
    session = _sessions.pop(user_id, None)
    if session and session.current_poll_id:
        unregister_poll(session.current_poll_id)
    return session


def end_group_session(chat_id: int) -> GroupQuizSession | None:
    cancel_group_timer(chat_id)
    session = _group_sessions.pop(chat_id, None)
    if session and session.current_poll_id:
        unregister_poll(session.current_poll_id)
    return session
