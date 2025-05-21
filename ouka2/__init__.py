import dotenv

dotenv.load_dotenv()
import os
import typing as t

__all__ = ("TOKEN", "OWNER_ID", "CUTEGIRLS_PARENT",)

TOKEN: t.Final = os.getenv("BOT_TOKEN")
OWNER_ID: t.Final = int(os.getenv("OWNER_ID", 0))
CUTEGIRLS_PARENT: t.Final = os.getenv("CUTEGIRLS_PARENT")
