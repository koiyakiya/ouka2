"""A script to handle Google Drive API operations and their relation with the SQLite database."""

from ouka2.utils import GoogleDrive, Tag, ID
from ouka2.utils.exceptions import *
import aiosqlite, sqlite3

class Cutegirls:
    @staticmethod
    async def ADD(
        image: bytes,
        user_id: int,
        file_name: str,
        mime_type: str,
        db: aiosqlite.Connection,
        drive: GoogleDrive,
        *,
        tags: list[Tag],
    ) -> ID:
        try:
            id = await drive.upload(
                image,
                file_name,
                mime_type
            )
            await db.execute(
                "INSERT INTO images (id, user_id, file_name, mime_type, file_size) VALUES (?, ?, ?, ?, ?)",
                (id, user_id, file_name, mime_type, len(image),),
            )
            await  db.commit()
            if tags:
                for tag in tags:
                    await db.execute(
                        "INSERT INTO image_tags (image_id, tag_id) VALUES (?, ?)",
                        (id, tag.id,),
                    )
            return id
        except sqlite3.Error as e:
            raise DatabaseAdditionError(
                f"Failed to add image to Google Drive and Database:  {e}"
            )
        except Exception as e:
            raise DatabaseException(
                f"big error!!!!: {e}"
            )