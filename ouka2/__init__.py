import dotenv

dotenv.load_dotenv()
import os
import typing as t

__all__ = ("TOKEN",)

TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID", 0))
