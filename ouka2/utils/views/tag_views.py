import miru
import hikari
import aiosqlite
from ouka2.utils import TagManager


class TagErrorCreationView(miru.View):
    def __init__(
        self, tag_name: str, db: aiosqlite.Connection, *args, **kwargs
    ) -> None:
        super().__init__(*args, **kwargs)
        self.tag_name = tag_name
        self.db = db

    @miru.button(label="Create", style=hikari.ButtonStyle.SUCCESS)
    async def create_tag(self, ctx: miru.ViewContext, button: miru.Button) -> None:
        if await TagManager.exists(self.tag_name, self.db):
            await ctx.respond(
                f"❌ Tag `{self.tag_name}` already exists. Please choose a different name. ❌",
                flags=hikari.MessageFlag.EPHEMERAL,
            )
            return
        await TagManager.create_tag(self.tag_name, ctx.user.id, self.db)
        await ctx.respond(
            f"Tag `{self.tag_name}` created successfully! 🎉",
            flags=hikari.MessageFlag.EPHEMERAL,
        )
