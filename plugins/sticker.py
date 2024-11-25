import imghdr
import math
import os
from asyncio import gather
from traceback import format_exc
from typing import List

from PIL import Image
from pyrogram import *
from pyrogram.enums import *
from pyrogram.errors import *
from pyrogram.file_id import *
from pyrogram.raw.functions.messages import *
from pyrogram.raw.functions.stickers import *
from pyrogram.raw.types import *
from pyrogram.types import *

from YukkiMusic import app
from utils.error import capture_err

BOT_USERNAME = app.username

MAX_STICKERS = (
    120  # would be better if we could fetch this limit directly from telegram
)
SUPPORTED_TYPES = ["jpeg", "png", "webp"]
STICKER_DIMENSIONS = (512, 512)


async def get_sticker_set_by_name(
    client: Client, name: str
) -> raw.base.messages.StickerSet:
    try:
        return await client.invoke(
            raw.functions.messages.GetStickerSet(
                stickerset=raw.types.InputStickerSetShortName(short_name=name),
                hash=0,
            )
        )
    except errors.exceptions.not_acceptable_406.StickersetInvalid:
        return None


# Known errors: (I don't see a reason to catch them as we, for sure, won't face them right now):
# errors.exceptions.bad_request_400.PackShortNameInvalid -> pack name needs to end with _by_botname
# errors.exceptions.bad_request_400.ShortnameOccupyFailed -> pack's name
# is already in use


async def create_sticker_set(
    client: Client,
    owner: int,
    title: str,
    short_name: str,
    stickers: List[raw.base.InputStickerSetItem],
) -> raw.base.messages.StickerSet:
    return await client.invoke(
        raw.functions.stickers.CreateStickerSet(
            user_id=await client.resolve_peer(owner),
            title=title,
            short_name=short_name,
            stickers=stickers,
        )
    )


async def add_sticker_to_set(
    client: Client,
    stickerset: raw.base.messages.StickerSet,
    sticker: raw.base.InputStickerSetItem,
) -> raw.base.messages.StickerSet:
    return await client.invoke(
        raw.functions.stickers.AddStickerToSet(
            stickerset=raw.types.InputStickerSetShortName(
                short_name=stickerset.set.short_name
            ),
            sticker=sticker,
        )
    )


async def create_sticker(
    sticker: raw.base.InputDocument, emoji: str
) -> raw.base.InputStickerSetItem:
    return raw.types.InputStickerSetItem(document=sticker, emoji=emoji)


async def resize_file_to_sticker_size(file_path: str) -> str:
    im = Image.open(file_path)
    if (im.width, im.height) < STICKER_DIMENSIONS:
        size1 = im.width
        size2 = im.height
        if im.width > im.height:
            scale = STICKER_DIMENSIONS[0] / size1
            size1new = STICKER_DIMENSIONS[0]
            size2new = size2 * scale
        else:
            scale = STICKER_DIMENSIONS[1] / size2
            size1new = size1 * scale
            size2new = STICKER_DIMENSIONS[1]
        size1new = math.floor(size1new)
        size2new = math.floor(size2new)
        sizenew = (size1new, size2new)
        im = im.resize(sizenew)
    else:
        im.thumbnail(STICKER_DIMENSIONS)
    try:
        os.remove(file_path)
        file_path = f"{file_path}.png"
        return file_path
    finally:
        im.save(file_path)


async def upload_document(
    client: Client, file_path: str, chat_id: int
) -> raw.base.InputDocument:
    media = await client.invoke(
        raw.functions.messages.UploadMedia(
            peer=await client.resolve_peer(chat_id),
            media=raw.types.InputMediaUploadedDocument(
                mime_type=client.guess_mime_type(file_path) or "application/zip",
                file=await client.save_file(file_path),
                attributes=[
                    raw.types.DocumentAttributeFilename(
                        file_name=os.path.basename(file_path)
                    )
                ],
            ),
        )
    )
    return raw.types.InputDocument(
        id=media.document.id,
        access_hash=media.document.access_hash,
        file_reference=media.document.file_reference,
    )


async def get_document_from_file_id(
    file_id: str,
) -> raw.base.InputDocument:
    decoded = FileId.decode(file_id)
    return raw.types.InputDocument(
        id=decoded.media_id,
        access_hash=decoded.access_hash,
        file_reference=decoded.file_reference,
    )


@app.on_message(filters.command("stickerid"))
@capture_err
async def sticker_id(_, message: Message):
    reply = message.reply_to_message

    if not reply:
        return await message.reply("Reply to a sticker.")

    if not reply.sticker:
        return await message.reply("Reply to a sticker.")

    await message.reply_text(f"`{reply.sticker.file_id}`")


@app.on_message(filters.command("getsticker"))
@capture_err
async def sticker_image(_, message: Message):
    r = message.reply_to_message

    if not r:
        return await message.reply("Reply to a sticker.")

    if not r.sticker:
        return await message.reply("Reply to a sticker.")

    m = await message.reply("Sending..")
    f = await r.download(f"{r.sticker.file_unique_id}.png")

    await gather(
        *[
            message.reply_photo(f),
            message.reply_document(f),
        ]
    )

    await m.delete()
    os.remove(f)


@app.on_message(filters.command("kang"))
@capture_err
async def _(self: app, message):
    prog_msg = await message.reply("Processing...")
    sticker_emojis = "🤔"
    sticker_emoji = message.command[1] if len(message.command) > 1 else sticker_emojis
    packnum = 0
    packname_found = False
    resize = False
    animated = False
    videos = False
    convert = False
    reply = message.reply_to_message
    user = await self.resolve_peer(message.from_user.username or message.from_user.id)

    if reply and reply.media:
        if reply.photo:
            resize = True
        elif reply.animation:
            videos = True
            convert = True
        elif reply.video:
            convert = True
            videos = True
        elif reply.document:
            if "image" in reply.document.mime_type:
                # mime_type: image/webp
                resize = True
            elif reply.document.mime_type in (
                enums.MessageMediaType.VIDEO,
                enums.MessageMediaType.ANIMATION,
            ):
                # mime_type: application/video
                videos = True
                convert = True
            elif "tgsticker" in reply.document.mime_type:
                # mime_type: application/x-tgsticker
                animated = True
        elif reply.sticker:
            if not reply.sticker.file_name:
                return await prog_msg.edit_text("Stiker tidak memiliki nama.")
            if reply.sticker.emoji:
                sticker_emoji = reply.sticker.emoji
            animated = reply.sticker.is_animated
            videos = reply.sticker.is_video
            if videos:
                convert = False
            elif not reply.sticker.file_name.endswith(".tgs"):
                resize = True
        else:
            return await prog_msg.edit_text()

        pack_prefix = "anim" if animated else "vid" if videos else "a"
        packname = f"{pack_prefix}_{message.from_user.id}_by_{self.me.username}"

        if (
            len(message.command) > 1
            and message.command[1].isdigit()
            and int(message.command[1]) > 0
        ):
            # provide pack number to kang in desired pack
            packnum = message.command.pop(1)
            packname = (
                f"{pack_prefix}{packnum}_{message.from_user.id}_by_{self.me.username}"
            )
        if len(message.command) > 1:
            # matches all valid emojis in input
            sticker_emoji = (
                "".join(set(EMOJI_PATTERN.findall("".join(message.command[1:]))))
                or sticker_emoji
            )
        filename = await self.download_media(message.reply_to_message)
        if not filename:
            # Failed to download
            await prog_msg.delete()
            return
    elif message.entities and len(message.entities) > 1:
        pack_prefix = "a"
        filename = "sticker.png"
        packname = f"c{message.from_user.id}_by_{self.me.username}"
        img_url = next(
            (
                message.text[y.offset : (y.offset + y.length)]
                for y in message.entities
                if y.type == "url"
            ),
            None,
        )

        if not img_url:
            await prog_msg.delete()
            return
        try:
            r = await http.get(img_url)
            if r.status_code == 200:
                with open(filename, mode="wb") as f:
                    f.write(r.read())
        except Exception as r_e:
            return await prog_msg.edit_text(f"{r_e.__class__.__name__} : {r_e}")
        if len(message.command) > 2:
            # m.command[1] is image_url
            if message.command[2].isdigit() and int(message.command[2]) > 0:
                packnum = message.command.pop(2)
                packname = f"a{packnum}_{message.from_user.id}_by_{self.me.username}"
            if len(message.command) > 2:
                sticker_emoji = (
                    "".join(set(EMOJI_PATTERN.findall("".join(message.command[2:]))))
                    or sticker_emoji
                )
            resize = True
    else:
        return await prog_msg.edit_text(
            "Ingin saya menebak stikernya? Harap tandai stiker."
        )
    try:
        if resize:
            filename = resize_image(filename)
        elif convert:
            filename = await convert_video(filename)
            if filename is False:
                return await prog_msg.edit_text("Error")
        max_stickers = 50 if animated else 120
        while not packname_found:
            try:
                stickerset = await self.invoke(
                    GetStickerSet(
                        stickerset=InputStickerSetShortName(short_name=packname),
                        hash=0,
                    )
                )
                if stickerset.set.count >= max_stickers:
                    packnum += 1
                    packname = f"{pack_prefix}_{packnum}_{message.from_user.id}_by_{self.me.username}"
                else:
                    packname_found = True
            except StickersetInvalid:
                break
        file = await self.save_file(filename)
        media = await self.invoke(
            SendMedia(
                peer=(await self.resolve_peer(dump)),
                media=InputMediaUploadedDocument(
                    file=file,
                    mime_type=self.guess_mime_type(filename),
                    attributes=[DocumentAttributeFilename(file_name=filename)],
                ),
                message=f"#Sticker kang by UserID -> {message.from_user.id}",
                random_id=self.rnd_id(),
            ),
        )
        msg_ = media.updates[-1].message
        stkr_file = msg_.media.document
        if packname_found:
            await prog_msg.edit_text("Menggunakan paket stiker yang ada...")
            await self.invoke(
                AddStickerToSet(
                    stickerset=InputStickerSetShortName(short_name=packname),
                    sticker=InputStickerSetItem(
                        document=InputDocument(
                            id=stkr_file.id,
                            access_hash=stkr_file.access_hash,
                            file_reference=stkr_file.file_reference,
                        ),
                        emoji=sticker_emoji,
                    ),
                )
            )
        else:
            await prog_msg.edit_text("Membuat paket stiker baru...")
            stkr_title = f"{message.from_user.first_name}"
            if animated:
                stkr_title += " AnimPack"
            elif videos:
                stkr_title += " VidPack"
            if packnum != 0:
                stkr_title += f" v{packnum}"
            try:
                await self.invoke(
                    CreateStickerSet(
                        user_id=user,
                        title=stkr_title,
                        short_name=packname,
                        stickers=[
                            InputStickerSetItem(
                                document=InputDocument(
                                    id=stkr_file.id,
                                    access_hash=stkr_file.access_hash,
                                    file_reference=stkr_file.file_reference,
                                ),
                                emoji=sticker_emoji,
                            )
                        ],
                        animated=animated,
                        videos=videos,
                    )
                )
            except PeerIdInvalid:
                return (
                    await prog_msg.edit_text(
                        "Tampaknya Anda belum pernah berinteraksi dengan saya dalam obrolan pribadi, Anda harus melakukannya dulu.."
                    ),
                )
    except BadRequest:
        return await prog_msg.edit_text(
            "Paket Stiker Anda penuh jika paket Anda tidak dalam Tipe v1 /kang 1, jika tidak dalam Tipe v2 /kang 2 dan seterusnya."
        )
    except Exception as all_e:
        return await prog_msg.edit_text(f"{all_e.__class__.__name__} : {all_e}")
    else:
        await prog_msg.edit_text(
            f"<b>Sticker Anda Berhasil Dibuat!</b>\n<b><a href=https://t.me/addstickers/{packname}>👀 Lihat Paket Sticker Disini</a></b>\n<b>Emoji:</b> {sticker_emoji}"
        )
        await self.delete_messages(chat_id=dump, message_ids=msg_.id, revoke=True)
        try:
            os.remove(filename)
        except OSError:
            pass
    return


@app.on_message(filters.command("kang"))
@capture_err
async def _(self, m):
    rep = m.reply_to_message.sticker

    try:
        sticker_id = rep.file_id
        decoded = FileId.decode(sticker_id)
        sticker = InputDocument(
            id=decoded.media_id,
            access_hash=decoded.access_hash,
            file_reference=decoded.file_reference,
        )
        await app.invoke(RemoveStickerFromSet(sticker=sticker))
        await m.reply(f"Stiker berhasil dihapus dari paket Anda.")
        return
    except Exception as e:
        await m.reply(
            f"Gagal menghapus stiker dari paket Anda.\n\nError: <code>{e}</code>"
        )
        return


__MODULE__ = "Sᴛɪᴄᴋᴇʀ"
__HELP__ = """
**COMMANDS:**

• /stickerid - **ɢᴇᴛs ᴛʜᴇ ғɪʟᴇ ɪᴅ ᴏғ ᴀɴʏ ʀᴇᴘʟɪᴇᴅ sᴛɪᴄᴋᴇʀ.**
• /getsticker - **ɢᴇᴛs ᴛʜᴇ ɪᴍᴀɢᴇ ᴏғ ᴀɴʏ ʀᴇᴘʟɪᴇᴅ sᴛɪᴄᴋᴇʀ.**
• /kang - **ᴋᴀɴɢs ᴀɴʏ sᴛɪᴄᴋᴇʀ ɪɴ ᴛʜᴇ ʏᴏᴜ ᴘᴀᴄᴋ**

**INFO:**

- ᴛʜɪs ʙᴏᴛ ᴀʟʟᴏᴡs ᴜsᴇʀs ᴛᴏ ɢᴇᴛ ᴛʜᴇ ғɪʟᴇ ɪᴅ ᴏʀ ᴛʜᴇ ɪᴍᴀɢᴇ ᴏғ ᴀɴʏ sᴛɪᴄᴋᴇʀ ᴛʜᴀᴛ ɪs ʀᴇᴘʟɪᴇᴅ ᴛᴏ ᴀ ᴍᴇssᴀɢᴇ, ᴀɴᴅ ᴀʟsᴏ ᴀʟʟᴏᴡs ᴜsᴇʀs ᴛᴏ ᴋᴀɴɢ ᴀɴʏ sᴛɪᴄᴋᴇʀ ɪɴ ᴛʜᴇ ᴄʜᴀᴛ ᴀɴᴅ ᴀᴅᴅ ɪᴛ ᴛᴏ ᴀ sᴛɪᴄᴋᴇʀ ᴘᴀᴄᴋ.
"""
