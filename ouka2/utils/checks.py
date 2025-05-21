import arc
from typing import Any
from ouka2 import OWNER_ID


def is_owner(ctx: arc.Context[Any]) -> None:
    if ctx.author.id != OWNER_ID:
        raise arc.errors.NotOwnerError(
            "You are not the owner of this bot. You cannot use this command."
        )
