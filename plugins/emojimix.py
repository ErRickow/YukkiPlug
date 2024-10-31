import requests
import tempfile
from pyrogram import Client, filters

from YukkiMusic import app
from YukkiMusic.utils.err import erornya

@app.on_message(filters.command("emomix"))
@erornya
def emojimix(client, message):
    # Mengambil emoji dari pesan
    emoji1 = message.command[1] if len(message.command) > 1 else None
    emoji2 = message.command[2] if len(message.command) > 2 else None

    if not emoji1 or not emoji2:
        message.reply("Silakan berikan dua emoji yang ingin digabungkan. Contoh: /emomix 😭 🟿")
        return

    # URL untuk menggabungkan emoji
    url = f"https://widipe.com/emojimix?emoji1={emoji1}&emoji2={emoji2}"

    try:
        response = requests.get(url)
        response.raise_for_status()  # Memastikan tidak ada error

        # Anda perlu mengekstrak URL stiker dari halaman yang diambil
        # Misalnya menggunakan BeautifulSoup (tidak ditampilkan di sini)

        sticker_url = url  # Ganti dengan URL stiker yang valid

        # Mengunduh gambar stiker
        sticker_response = requests.get(sticker_url)
        sticker_response.raise_for_status()

        # Simpan stiker ke file sementara
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_file:
            temp_file.write(sticker_response.content)
            temp_file_path = temp_file.name

        # Mengirimkan stiker dengan send_photo
        client.send_photo(chat_id=message.chat.id, photo=temp_file_path)
    except requests.RequestException as e:
        message.reply(f"Terjadi kesalahan saat menggabungkan emoji: {e}")

