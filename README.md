# Avtotest Telegram Bot

Haydovchilik imtihoniga tayyorgarlik uchun Telegram bot (600 ta savol).

## Imkoniyatlar

- **Kunlik savollar** — har kuni avtomatik quiz savollari
- **Tez test** — 10 ta tasodifiy savol
- **Imtihon** — 20 ta savol (86% o'tish balli)
- **Bilet bo'yicha** — bilet raqami tanlab mashq
- **Telegram Quiz** — chiroyli native quiz ko'rinishi
- **Rasmli savollar** — avtotestu.uz dan rasm yuboriladi
- **Statistika** — javoblar va natijalar
- **3 til** — o'zbek (lotin/kiril), rus

## O'rnatish

```bash
pip install -r requirements.txt
```

## Ishga tushirish

Loyiha papkasida (`mybot2`) turib:

```bash
python run.py
```

yoki:

```bash
python -m bot.main
```

## Sozlamalar (.env)

| O'zgaruvchi | Tavsif | Default |
|---|---|---|
| `BOT_TOKEN` | Telegram bot tokeni | — |
| `IMAGE_BASE_URL` | Savol rasmlari bazasi | `https://www.avtotestu.uz/images` |
| `DAILY_QUIZ_HOUR` | Kunlik savol soati | `9` |
| `DAILY_QUESTIONS_COUNT` | Kunlik savollar soni | `5` |

Rasmlar `600.json` dagi `media_url` (masalan `u1uz.webp`) orqali yuklanadi:
`https://www.avtotestu.uz/images/u1uz.webp`


pip install -r requirements.txt