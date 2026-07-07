from dotenv import load_dotenv
import os

load_dotenv()

KITE_API_KEY = os.getenv("KITE_API_KEY")
KITE_API_SECRET = os.getenv("KITE_API_SECRET")
KITE_ACCESS_TOKEN = os.getenv("KITE_ACCESS_TOKEN")

DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK")

DATABASE_URL = os.getenv("DATABASE_URL")