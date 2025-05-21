import hikari, arc, aiosqlite
from ouka2.utils import TagManager
from ouka2.utils.exceptions import *
from ouka2.utils.views import TagErrorCreationView
import miru

plugin = arc.GatewayPlugin("cutegirls")

cutegirls = plugin.include_slash_group("cutegirls")
tags = cutegirls.include_subgroup("tags")

async def provide_opts(
    data: arc.AutocompleteData[arc.GatewayClient, str],
    db: aiosqlite.Connection = arc.inject(),
) -> list[str]:
    query = data.focused_value
    if not query:
        return []
    cursor = await db.execute(
        "SELECT name FROM tags WHERE name LIKE ?", (f"%{query}%",)
    )
    rows = await cursor.fetchall()
    return [row[0] for row in rows]


@tags.include
@arc.slash_subcommand("create", "Create a new tag 🤩💖")
async def create_tag(
    ctx: arc.GatewayContext,
    name: arc.Option[str, arc.StrParams("The tag name❓🤔")],
    db: aiosqlite.Connection = arc.inject(),
) -> None:
    await TagManager.create_tag(name, ctx.author.id, db)
    await ctx.respond(
        f"Tag `{name}` created successfully! 🎉", flags=hikari.MessageFlag.EPHEMERAL
    )


@tags.include
@arc.slash_subcommand("delete", "Delete an existing tag 🥲")
async def delete_tag(
    ctx: arc.GatewayContext,
    name: arc.Option[
        str, arc.StrParams("The tag name❓🤔", autocomplete_with=provide_opts)
    ],
    db: aiosqlite.Connection = arc.inject(),
) -> None:
    await TagManager.delete_tag(name, db)
    await ctx.respond(
        f"Tag `{name}` deleted successfully! 🎉", flags=hikari.MessageFlag.EPHEMERAL
    )


@create_tag.set_error_handler
@delete_tag.set_error_handler
async def tag_error_handler(
    ctx: arc.GatewayContext,
    error: Exception,
    db: aiosqlite.Connection = arc.inject(),
    miru_client: miru.Client = arc.inject(),
) -> None:
    if isinstance(error, TagExistsError):
        await ctx.respond(
            f"❌ Tag `{error.tag_name}` already exists. Please choose a different name. ❌",
            flags=hikari.MessageFlag.EPHEMERAL,
        )
    elif isinstance(error, TagDoesNotExistError):
        view = TagErrorCreationView(error.tag_name, db)
        await ctx.respond(
            f"❌ Tag `{error.tag_name}` does not exist. Please check the name and try again. ❌",
            flags=hikari.MessageFlag.EPHEMERAL,
            components=view,
        )
        miru_client.start_view(view)
    elif isinstance(error, TagError):
        await ctx.respond(
            f"❌ An error occurred while processing your request. ❌",
            flags=hikari.MessageFlag.EPHEMERAL,
        )


@arc.loader
def loader(client: arc.GatewayClient) -> None:
    client.add_plugin(plugin)
