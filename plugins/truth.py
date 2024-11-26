from pyrogram import filters
from YukkiMusic import app

from ApiNyaEr import apinya

@app.on_message(filters.command("truth"))
def get_truth(client, message):
    try:
        truth_question = apinya.truth()
        message.reply_text(
            f"💡 **Truth Challenge** 💡\n\n"
            f"❓ **Pertanyaan**: {truth_question}"
        )
    except Exception as e:
        message.reply_text(
            "⚠️ Terjadi kesalahan saat mengambil pertanyaan Truth. Coba lagi nanti ya!"
        )


@app.on_message(filters.command("dare"))
def get_dare(client, message):
    try:
        dare_question = apinya.dare()
        message.reply_text(
            f"🔥 **Dare Challenge** 🔥\n\n"
            f"💪 **Tantangan**: {dare_question}"
        )
    except Exception as e:
        message.reply_text(
            "⚠️ Terjadi kesalahan saat mengambil tantangan Dare. Coba lagi nanti ya!"
        )

__HELP__ = """
**ᴛʀᴜᴛʜ ᴏʀ ᴅᴀʀᴇ ʙᴏᴛ ᴄᴏᴍᴍᴀɴᴅs**

ᴜsᴇ ᴛʜᴇsᴇ ᴄᴏᴍᴍᴀɴᴅs ᴛᴏ ᴘʟᴀʏ ᴛʀᴜᴛʜ ᴏʀ ᴅᴀʀᴇ:

- `/truth`: ɢᴇᴛ ᴀ ʀᴀɴᴅᴏᴍ ᴛʀᴜᴛʜ ǫᴜᴇsᴛɪᴏɴ. ᴀɴsᴡᴇʀ ʜᴏɴᴇsᴛʟʏ!
- `/dare`: ɢᴇᴛ ᴀ ʀᴀɴᴅᴏᴍ ᴅᴀʀᴇ ᴄʜᴀʟʟᴇɴɢᴇ. ᴄᴏᴍᴘʟᴇᴛᴇ ɪᴛ ɪғ ʏᴏᴜ ᴅᴀʀᴇ!

**ᴇxᴀᴍᴘʟᴇs:**
- `/truth`: "ᴡʜᴀᴛ ɪs ʏᴏᴜʀ ᴍᴏsᴛ ᴇᴍʙᴀʀʀᴀssɪɴɢ ᴍᴏᴍᴇɴᴛ?"
- `/dare`: "ᴅᴏ 10 ᴘᴜsʜ-ᴜᴘs."

**ɴᴏᴛᴇ:**
ɪғ ʏᴏᴜ ᴇɴᴄᴏᴜɴᴛᴇʀ ᴀɴʏ ɪssᴜᴇs ᴡɪᴛʜ ғᴇᴛᴄʜɪɴɢ ǫᴜᴇsᴛɪᴏɴs, ᴘʟᴇᴀsᴇ ᴛʀʏ ᴀɢᴀɪɴ ʟᴀᴛᴇʀ.
"""

__MODULE__ = "Tʀᴜᴛʜ"
