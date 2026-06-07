from dataclasses import dataclass, field

from bot.config import EXAM_QUESTIONS_COUNT, QUICK_QUIZ_COUNT
from bot.services.questions import Question, question_bank


@dataclass
class QuizSession:
    user_id: int
    quiz_type: str
    questions: list[Question] = field(default_factory=list)
    current_index: int = 0
    correct_count: int = 0
    answered: bool = False
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


_sessions: dict[int, QuizSession] = {}


def get_session(user_id: int) -> QuizSession | None:
    return _sessions.get(user_id)


def start_session(
    user_id: int,
    quiz_type: str,
    lang: str = "uz_lat",
    ticket_num: int | None = None,
) -> QuizSession:
    if quiz_type == "exam":
        questions = question_bank.get_random(EXAM_QUESTIONS_COUNT, lang)
    elif quiz_type == "quick":
        questions = question_bank.get_random(QUICK_QUIZ_COUNT, lang)
    elif quiz_type == "ticket" and ticket_num is not None:
        questions = question_bank.get_by_ticket(ticket_num, lang)
    elif quiz_type == "daily":
        from bot.config import DAILY_QUESTIONS_COUNT

        questions = question_bank.get_daily_questions(DAILY_QUESTIONS_COUNT, lang)
    else:
        questions = question_bank.get_random(QUICK_QUIZ_COUNT, lang)

    session = QuizSession(
        user_id=user_id,
        quiz_type=quiz_type,
        questions=questions,
        lang=lang,
    )
    _sessions[user_id] = session
    return session


def end_session(user_id: int) -> QuizSession | None:
    return _sessions.pop(user_id, None)
