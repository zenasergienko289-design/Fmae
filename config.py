import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
BOT_USERNAME = os.getenv("BOT_USERNAME", "offersssa_bot")

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN не задан в .env")
