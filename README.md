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
- **Guruh rejimi** — guruhda birgalikda test ishlash

## Guruh buyruqlari

Botni guruhga qo'shing va buyruqlardan foydalaning:

- `/test` — guruh tez testi (10 savol)
- `/imtihon` — guruh imtihoni (20 savol)
- `/natija` — joriy natijalar jadvali
- `/stop` — testni to'xtatish

## O'rnatish (venv)

### Linux / server

```bash
chmod +x scripts/setup.sh scripts/start.sh
./scripts/setup.sh
# .env faylida BOT_TOKEN ni yozing
./scripts/start.sh
```

### Windows

```bat
scripts\setup.bat
REM .env faylida BOT_TOKEN ni yozing
scripts\start.bat
```

### Qo'lda

```bash
python -m venv venv
# Linux: source venv/bin/activate
# Windows: venv\Scripts\activate
python -m pip install -r requirements.txt
python run.py
```

## Serverda 24/7 ishlatish (systemd)

```bash
sudo useradd -r -m -s /bin/bash botuser
sudo mkdir -p /opt/avtotestubot
sudo cp -r . /opt/avtotestubot/
sudo chown -R botuser:botuser /opt/avtotestubot

cd /opt/avtotestubot
sudo -u botuser ./scripts/setup.sh
sudo -u botuser nano .env   # BOT_TOKEN yozing

sudo cp deploy/avtotestubot.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable avtotestubot
sudo systemctl start avtotestubot
sudo systemctl status avtotestubot
```

Loglar: `journalctl -u avtotestubot -f`

**Muhim:** bir vaqtning o'zida faqat bitta bot nusxasi ishlashi kerak (local + server birga bo'lmasin).

## Sozlamalar (.env)

| O'zgaruvchi | Tavsif | Default |
|---|---|---|
| `BOT_TOKEN` | Telegram bot tokeni | — |
| `IMAGE_BASE_URL` | Savol rasmlari bazasi | `https://www.avtotestu.uz/images` |
| `DAILY_QUIZ_HOUR` | Kunlik savol soati | `9` |
| `DAILY_QUESTIONS_COUNT` | Kunlik savollar soni | `5` |
| `QUIZ_QUESTION_TIMEOUT` | Har bir savol vaqti (soniya) | `60` |
| `WEBAPP_URL` | Sayt / Web App manzili | `https://avtotestu.uz` |
| `PRO_CONTACT` | PRO obuna admini | `@avtotestu_ad` |

## PRO obuna

Botda **✦ PRO Obuna** bo'limi va **🔐 Kirish** tugmasi mavjud.
Kirish tugmasi Telegram Web App orqali saytni ochadi.
Obuna narxlari bot ichida ko'rsatiladi, to'lov sayt orqali amalga oshiriladi.

Rasmlar `600.json` dagi `media_url` (masalan `u1uz.webp`) orqali yuklanadi:
`https://www.avtotestu.uz/images/u1uz.webp`

## Bot buyruqlari

- `/start` — bosh menyu
- `/stop` — testni to'xtatish
- `/help` — yordam
