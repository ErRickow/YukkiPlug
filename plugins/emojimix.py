import requests
from pyrogram import Client, filters

from YukkiMusic import app

@app.on_message(filters.command("emomix"))
def emojimix(client, message):
    # Mengambil emoji dari pesan
    emoji1 = message.command[1] if len(message.command) > 1 else None
    emoji2 = message.command[2] if len(message.command) > 2 else None

    if not emoji1 or not emoji2:
        message.reply("Silakan berikan dua emoji yang ingin digabungkan. Contoh: /emomix 😭 🟿")
        return

    url = f"https://widipe.com/emojimix?emoji1={emoji1}&emoji2={emoji2}"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Memastikan tidak ada error
        result_message = "Emoji gabungan berhasil dibuat! [Lihat di sini](" + url + ")"
        message.reply(result_message, disable_web_page_preview=True)
    except requests.RequestException as e:
        message.reply(f"Terjadi kesalahan saat menggabungkan emoji: {e}")

# Menjalankan bot
app.run()
