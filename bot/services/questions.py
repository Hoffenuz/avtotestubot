import json
import random
from dataclasses import dataclass

from bot.config import DEFAULT_LANG, IMAGE_BASE_URL, QUESTIONS_FILE


@dataclass
class Question:
    global_id: str
    ticket_num: int
    order: int
    text: str
    options: list[str]
    correct_index: int
    media_url: str = ""

    @property
    def image_url(self) -> str | None:
        if not self.media_url:
            return None
        return f"{IMAGE_BASE_URL}/{self.media_url.lstrip('/')}"


class QuestionBank:
    def __init__(self) -> None:
        self._raw: list[dict] = []
        self._loaded = False

    def load(self) -> None:
        if self._loaded:
            return
        with open(QUESTIONS_FILE, encoding="utf-8") as f:
            self._raw = json.load(f)
        self._loaded = True

    @property
    def total(self) -> int:
        self.load()
        return len(self._raw)

    def _parse(self, item: dict, lang: str) -> Question | None:
        content = item.get("content", {}).get(lang) or item.get("content", {}).get(
            DEFAULT_LANG
        )
        if not content:
            return None

        options = content.get("options", [])
        correct_index = next(
            (i for i, opt in enumerate(options) if opt.get("is_correct")), 0
        )

        return Question(
            global_id=item["task_info"]["global_id"],
            ticket_num=item["task_info"]["ticket_num"],
            order=item["task_info"]["order"],
            text=content["text"],
            options=[opt["text"] for opt in options],
            correct_index=correct_index,
            media_url=item.get("media_url", ""),
        )

    def get_by_id(self, global_id: str, lang: str = DEFAULT_LANG) -> Question | None:
        self.load()
        for item in self._raw:
            if item["task_info"]["global_id"] == global_id:
                return self._parse(item, lang)
        return None

    def get_random(self, count: int, lang: str = DEFAULT_LANG) -> list[Question]:
        self.load()
        sample = random.sample(self._raw, min(count, len(self._raw)))
        result = []
        for item in sample:
            q = self._parse(item, lang)
            if q:
                result.append(q)
        return result

    def get_by_ticket(
        self, ticket_num: int, lang: str = DEFAULT_LANG
    ) -> list[Question]:
        self.load()
        items = [
            item
            for item in self._raw
            if item["task_info"]["ticket_num"] == ticket_num
        ]
        result = []
        for item in items:
            q = self._parse(item, lang)
            if q:
                result.append(q)
        return result

    def get_daily_questions(
        self, count: int, lang: str = DEFAULT_LANG
    ) -> list[Question]:
        return self.get_random(count, lang)

    def ticket_numbers(self) -> list[int]:
        self.load()
        return sorted({item["task_info"]["ticket_num"] for item in self._raw})


question_bank = QuestionBank()
