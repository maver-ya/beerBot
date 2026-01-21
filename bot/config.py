import os
from dotenv import load_dotenv

load_dotenv(dotenv_path='.env.dev')

BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is not set")
