from YukkiMusic import app
from pyrogram import filters
import nekos


@app.on_message(filters.command("hug"))
async def huggg(client, message):
    try:
        if message.reply_to_message:
            await message.reply_video(
                nekos.img("hug"),
                caption=f"{message.from_user.mention} hugged {message.reply_to_message.from_user.mention}",
            )
        else:
            await message.reply_video(nekos.img("hug"))
    except Exception as e:
        await message.reply_text(f"Error: {e}")


__MODULE__ = "Hᴜɢ"
__HELP__ = """
Bᴏᴛ ɪɴɪ ʀᴇsᴘᴏɴ ᴛᴏ ᴄᴏᴍᴍᴀɴᴅs ᴅɪ ʙᴀᴡᴀʜ ɪɴɪ:

- /hug: Mᴇɴɢɪʀɪᴋᴀɴ ᴀɴɪᴍᴀᴛɪᴏɴ ʜᴜɢ.

**Cᴏᴍᴍᴀɴᴅs**

- /hug: Mᴇɴɢɪʀɪᴋᴀɴ ᴀɴɪᴍᴀᴛɪᴏɴ ʜᴜɢ. Jɪᴋᴀ ᴅɪᴘᴜᴛʜᴛᴜᴋᴀɴ sᴇʙᴀɪᴋ ᴍᴇssᴀɢᴇ, ɪᴛ ᴍᴇɴᴛɪᴏɴs ᴛʜᴇ sᴇɴᴅᴇʀ ᴀɴᴅ ʀᴇᴄɪᴘɪᴇɴᴛ ᴏғ ᴛʜᴇ ʜᴜɢ.

**Cᴀʀᴀ Mᴇɴɢɢᴜɴᴀᴋᴀɴ**

- Gᴜɴᴀᴋᴀɴ /hug ᴜɴᴛᴜᴋ ᴍᴇɴɢɪʀɪᴋᴀɴ ᴀɴɪᴍᴀᴛɪᴏɴ ʜᴜɢ.
- Rᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇssᴀɢᴇ ᴡɪᴛʜ /hug ᴜɴᴛᴜᴋ ᴍᴇɴɢɪʀɪᴋᴀɴ ᴀɴɪᴍᴀᴛɪᴏɴ ʜᴜɢ ᴍᴇɴᴛɪᴏɴɪɴɢ ᴛʜᴇ sᴇɴᴅᴇʀ ᴀɴᴅ ʀᴇᴄɪᴘɪᴇɴᴛ.

**Nᴏᴛᴇs**

- Pᴀsᴛɪᴋᴀɴ sᴇᴛᴛɪɴɢ ᴄʜᴀᴛ ᴋᴀʜ ᴀʟʟᴏᴡ ʙᴏᴛ ᴜɴᴛᴜᴋ sᴇɴᴅ ᴠɪᴅᴇᴏs/sᴛɪᴄᴋᴇʀs sᴇʙᴀɪᴋ ʀᴇᴘʟɪᴇs ᴜɴᴛᴜᴋ ʜᴜɴᴜᴘ.
"""
