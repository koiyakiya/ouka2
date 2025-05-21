import aiosqlite
import sqlite3
from ouka2.utils.exceptions import *
from dataclasses import dataclass


@dataclass
class Tag:
    name: str
    creator_id: int


class TagManager:
    """
    TagManager handles tag operations in the database.

    This class provides static methods for creating, deleting and checking existence
    of tags in the database. All operations are asynchronous and use aiosqlite for 
    database communication.

    ## Attributes:
        - None

    ## Methods:
        `create_tag(name, creator_id, db)`: Creates a new tag in the database
        `delete_tag(name, db)`: Deletes an existing tag from the database
        `exists(name, db)`: Checks if a tag exists in the database
    """
    @staticmethod
    async def create_tag(name: str, creator_id: int, db: aiosqlite.Connection) -> Tag:
        """
        Creates a new tag in the database.
        
        Args:
            name (str): The name of the tag to create
            creator_id (int): The ID of the user creating the tag
            db (aiosqlite.Connection): Database connection
            
        Returns:
            Tag: A Tag object representing the newly created tag
            
        Raises:
            TagExistsError: If a tag with the same name already exists
            TagCreationError: If there's an error during tag creation
        """
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
    async def delete_tag(name: str, db: aiosqlite.Connection) -> None:
        """
        Deletes a tag from the database.
        
        Args:
            name (str): The name of the tag to delete
            db (aiosqlite.Connection): Database connection
            
        Raises:
            TagDoesNotExistError: If the tag doesn't exist
            TagCreationError: If there's an error during tag deletion
        """
        try:
            if not await TagManager.exists(name, db):
                raise TagDoesNotExistError(name)
            await db.execute("DELETE FROM tags WHERE name = ?", (name,))
            await db.commit()
        except sqlite3.Error as e:
            raise TagCreationError(f"Failed to delete tag: {e}")

    @staticmethod
    async def exists(name: str, db: aiosqlite.Connection) -> bool:
        """
        Checks if a tag exists in the database.
        
        Args:
            name (str): The name of the tag to check
            db (aiosqlite.Connection): Database connection
            
        Returns:
            bool: True if the tag exists, False otherwise
            
        Raises:
            TagError: If there's an error checking tag existence
        """
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
