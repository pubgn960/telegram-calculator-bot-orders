import logging
import os
import psycopg2

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    CommandHandler,
    ContextTypes,
    filters,
)
from sympy import sympify

logging.basicConfig(format="%(message)s", level=logging.INFO)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("telegram").setLevel(logging.WARNING)
logging.getLogger("apscheduler").setLevel(logging.WARNING)

DATABASE_URL = os.getenv("DATABASE_URL")

ALLOWED_USERS = [
    1573531032,
    6656261222,
    1408137192,
]


def get_connection():
    return psycopg2.connect(DATABASE_URL)


def init_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS group_totals(
        chat_id BIGINT PRIMARY KEY,
        total DOUBLE PRECISION DEFAULT 0
    )
    """)

    conn.commit()
    cur.close()
    conn.close()


def get_total(chat_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT total FROM group_totals WHERE chat_id=%s",
        (chat_id,)
    )

    row = cur.fetchone()

    cur.close()
    conn.close()

    return row[0] if row else 0


def save_total(chat_id, total):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO group_totals(chat_id,total)
    VALUES(%s,%s)
    ON CONFLICT(chat_id)
    DO UPDATE SET total=EXCLUDED.total
    """, (chat_id, total))

    conn.commit()

    cur.close()
    conn.close()


async def calculate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id not in ALLOWED_USERS:
        return

    chat_id = update.effective_chat.id

    if update.message.text:
        content = update.message.text
    elif update.message.caption:
        content = update.message.caption
    else:
        return

    before = get_total(chat_id)

    if content.strip() == "0":
        await update.message.reply_text(
            f"💰 Remaining Amount: {before}"
        )
        return

    now = 0

    for line in content.splitlines():
        line = line.strip()

        if not line:
            continue

        try:
            now += float(sympify(line))
        except Exception:
            continue

    if now == 0:
        return

    total = before + now

    save_total(chat_id, total)

    await update.message.reply_text(
        f"before: {before}\n"
        f"now: {now}\n"
        f"total: {total}"
    )


async def paid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ALLOWED_USERS:
        return

    chat_id = update.effective_chat.id

    previous = get_total(chat_id)

    save_total(chat_id, 0)

    await update.message.reply_text(
        f"✅ Payment Received\n\n"
        f"Paid Amount: {previous}\n"
        f"Remaining Amount: 0"
    )


async def myid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"👤 user_id: {update.effective_user.id}\n"
        f"💬 chat_id: {update.effective_chat.id}"
    )


def main():
    if not DATABASE_URL:
        raise Exception("DATABASE_URL environment variable not found!")

    init_db()

    token = os.getenv("TOKEN")

    if not token:
        raise Exception("TOKEN environment variable not found!")

    app = ApplicationBuilder().token(token).build()

    app.add_handler(CommandHandler("myid", myid))
    app.add_handler(CommandHandler("paid", paid))

    app.add_handler(
        MessageHandler(
            (filters.TEXT | filters.PHOTO | filters.VIDEO | filters.Document.ALL)
            & ~filters.COMMAND,
            calculate,
        )
    )

    print("Bot is running...")

    app.run_polling()


if __name__ == "__main__":
    main()
