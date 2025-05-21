import aiosqlite
import sqlite3
from ouka2.utils.exceptions import *
from dataclasses import dataclass


@dataclass
class Tag:
    name: str
    creator_id: int


class TagManager:
    @staticmethod
    async def create_tag(name: str, creator_id: int, db: aiosqlite.Connection) -> Tag:
        try:
            await db.execute(
                "INSERT INTO tags (name, creator_id) VALUES (?, ?)",
                (
                    name,
                    creator_id,
                ),
            )
            await db.commit()
            return Tag(name=name, creator_id=creator_id)
        except sqlite3.IntegrityError:
            raise TagExistsError(name)
        except sqlite3.Error as e:
            raise TagCreationError(f"Failed to create tag: {e}")

    @staticmethod
    async def delete_tag(name: str, db: aiosqlite.Connection) -> bool:
        try:
            if not await TagManager.exists(name, db):
                raise TagDoesNotExistError(name)
            cursor = await db.execute("DELETE FROM tags WHERE name = ?", (name,))
            await db.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            raise TagCreationError(f"Failed to delete tag: {e}")

    @staticmethod
    async def exists(name: str, db: aiosqlite.Connection) -> bool:
        try:
            cursor = await db.execute(
                "SELECT COUNT(*) FROM tags WHERE name = ?", (name,)
            )
            count = await cursor.fetchone()
            if count is None:
                return False
            return count[0] > 0
        except sqlite3.Error as e:
            raise TagError(f"Failed to check tag existence: {e}")
