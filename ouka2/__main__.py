import hikari
import arc
from ouka2 import TOKEN
from ouka2.utils import GoogleDriveAuth, GoogleDrive
import aiosqlite
import miru

if not TOKEN:
    raise ValueError("No token provided. Set the BOT_TOKEN environment variable.")

bot = hikari.GatewayBot(token=TOKEN)

client = arc.GatewayClient(bot)

miru_client = miru.Client.from_arc(client)

client.load_extensions_from("./ouka2/extensions")


@client.add_startup_hook
async def startup_hook(client: arc.GatewayClient) -> None:
    client.set_type_dependency(miru.Client, miru_client)
    auth_manager = GoogleDriveAuth()
    drive = GoogleDrive(auth_manager)
    await drive.initialize()
    client.set_type_dependency(GoogleDrive, drive)
    db = await aiosqlite.connect("./data/dynamic/ouka2.db")
    await db.execute("PRAGMA foreign_keys = ON;")
    await db.commit()
    with open("./data/static/build.sql", "r") as f:
        sql = f.read()
    await db.executescript(sql)
    client.set_type_dependency(aiosqlite.Connection, db)


@client.add_shutdown_hook
async def shutdown_hook(client: arc.GatewayClient) -> None:
    db: aiosqlite.Connection = client.get_type_dependency(aiosqlite.Connection)
    await db.close()


bot.run()
