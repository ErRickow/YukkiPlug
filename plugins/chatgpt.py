from pyrogram import filters
from pyrogram.enums import ChatAction
from ApiNyaEr import apinya

from YukkiMusic import app
from config import BANNED_USERS


@app.on_message(filters.command(["chatgpt", "ai", "ask"]) & ~BANNED_USERS)
async def chatgpt_chat(bot, message):
    if len(message.command) < 2 and not message.reply_to_message:
        await message.reply_text(
            "Example:\n\n`/ai write simple website code using html css, js?`"
        )
        return

    if message.reply_to_message and message.reply_to_message.text:
        user_input = message.reply_to_message.text
    else:
        user_input = " ".join(message.command[1:])

    await bot.send_chat_action(message.chat.id, ChatAction.TYPING)
    results = await apinya.ai(user_input)
    await message.reply_text(results)


__MODULE__ = "ChatGPT"
__HELP__ = """
/ai [pertanyaan] - Mengajukan pertanyaan ke AI
/gemini [Pertanyaan] - ajukan pertanyaan Anda dengan penyair Google Gemini"""