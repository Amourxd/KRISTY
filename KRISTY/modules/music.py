from __future__ import unicode_literals
import asyncio
import math
import io
import os
import time
import requests
import wget
import yt_dlp
from urllib.parse import urlparse
from pyrogram import filters
from pyrogram.types import Message
from tswift import Song
from yt_dlp import YoutubeDL
from youtube_search import YoutubeSearch
from youtubesearchpython import SearchVideos
from KRISTY.utils.pluginhelper import get_text, progress
from KRISTY import pbot, arq

async def lyrics_func(answers, text):
    song = await arq.lyrics(text)
    if not song.ok:
        answers.append(
            InlineQueryResultArticle(
                title="Error",
                description=song.result,
                input_message_content=InputTextMessageContent(
                    song.result
                ),
            )
        )
        return answers
    lyrics = song.result
    song = lyrics.splitlines()
    song_name = song[0]
    artist = song[1]
    if len(lyrics) > 4095:
        lyrics = await hastebin(lyrics)
        lyrics = f"**LYRICS_TOO_LONG:** [URL]({lyrics})"

    msg = f"**__{lyrics}__**"

    answers.append(
        InlineQueryResultArticle(
            title=song_name,
            description=artist,
            input_message_content=InputTextMessageContent(msg),
        )
    )
    return answers


def get_file_extension_from_url(url):
    url_path = urlparse(url).path
    basename = os.path.basename(url_path)
    return basename.split(".")[-1]


def download_youtube_audio(url: str):
    global is_downloading
    with yt_dlp.YoutubeDL(
        {
            "format": "bestaudio",
            "writethumbnail": True,
            "quiet": True,
        }
    ) as ydl:
        info_dict = ydl.extract_info(url, download=False)
        if int(float(info_dict["duration"])) > 180:
            is_downloading = False
            return []
        ydl.process_info(info_dict)
        audio_file = ydl.prepare_filename(info_dict)
        basename = audio_file.rsplit(".", 1)[-2]
        if info_dict["ext"] == "webm":
            audio_file_opus = basename + ".opus"
            ffmpeg.input(audio_file).output(
                audio_file_opus, codec="copy", loglevel="error"
            ).overwrite_output().run()
            os.remove(audio_file)
            audio_file = audio_file_opus
        thumbnail_url = info_dict["thumbnail"]
        thumbnail_file = (
            basename + "." + get_file_extension_from_url(thumbnail_url)
        )
        title = info_dict["title"]
        performer = info_dict["uploader"]
        duration = int(float(info_dict["duration"]))
    return [title, performer, duration, audio_file, thumbnail_file]


@pbot.on_message(filters.command(["vsong", "video"]))
async def ytmusic(client, message: Message):
    urlissed = get_text(message)

    pablo = await client.send_message(
        message.chat.id, f"`ɢᴇᴛᴛɪɴɢ {urlissed}  ꜰʀᴏᴍ ʏᴏᴜᴛᴜʙᴇ ꜱᴇʀᴠᴇʀꜱ. ᴘʟᴇᴀꜱᴇ ᴡᴀɪᴛ ʙᴀʙʏ🥀.`"
    )
    if not urlissed:
        await pablo.edit("ɪɴᴠᴀʟɪᴅ ᴄᴏᴍᴍᴀɴᴅ ꜱʏɴᴛᴀx, ᴘʟᴇᴀꜱᴇ ᴄʜᴇᴄᴋ ʜᴇʟᴘ ᴍᴇɴᴜ ᴛᴏ ᴋɴᴏᴡ ᴍᴏʀᴇ ʙᴀʙʏ🥀!")
        return

    search = SearchVideos(f"{urlissed}", offset=1, mode="dict", max_results=1)
    mi = search.result()
    mio = mi["search_result"]
    mo = mio[0]["link"]
    thum = mio[0]["title"]
    fridayz = mio[0]["id"]
    thums = mio[0]["channel"]
    kekme = f"https://img.youtube.com/vi/{fridayz}/hqdefault.jpg"
    await asyncio.sleep(0.6)
    url = mo
    sedlyf = wget.download(kekme)
    opts = {
        "format": "best",
        "addmetadata": True,
        "key": "FFmpegMetadata",
        "prefer_ffmpeg": True,
        "geo_bypass": True,
        "nocheckcertificate": True,
        "postprocessors": [{"key": "FFmpegVideoConvertor", "preferedformat": "mp4"}],
        "outtmpl": "%(id)s.mp4",
        "logtostderr": False,
        "quiet": True,
    }
    try:
        with YoutubeDL(opts) as ytdl:
            infoo = ytdl.extract_info(url, False)
            duration = round(infoo["duration"] / 60)
            ytdl_data = ytdl.extract_info(url, download=True)

    except Exception as e:
        await pablo.edit(f"**ꜰᴀɪʟᴇᴅ ᴛᴏ ᴅᴏᴡɴʟᴏᴀᴅ** \n**ᴇʀʀᴏʀ :** `{str(e)}` ʙᴀʙʏ🥀")
        return
    c_time = time.time()
    file_stark = f"{ytdl_data['id']}.mp4"
    capy = f"**Video Name ➠** [{thum}]({mo}) \n**Requested For :** `{urlissed}` \n**Channel :** `{thums}` "
    await client.send_video(
        message.chat.id,
        video=open(file_stark, "rb"),
        duration=int(ytdl_data["duration"]),
        file_name=str(ytdl_data["title"]),
        thumb=sedlyf,
        caption=capy,
        supports_streaming=True,
        progress=progress,
        progress_args=(
            pablo,
            c_time,
            f"`ᴜᴘʟᴏᴀᴅɪɴɢ {urlissed} ꜱᴏɴɢ ꜰʀᴏᴍ ʏᴏᴜᴛᴜʙᴇ ᴍᴜꜱɪᴄ ʙᴀʙʏ🥀!`",
            file_stark,
        ),
    )
    await pablo.delete()
    for files in (sedlyf, file_stark):
        if files and os.path.exists(files):
            os.remove(files)


@pbot.on_message(filters.command(["music", "song"]))
async def ytmusic(client, message: Message):
    urlissed = get_text(message)
    if not urlissed:
        await client.send_message(
            message.chat.id,
            "ɪɴᴠᴀʟɪᴅ ᴄᴏᴍᴍᴀɴᴅ ꜱʏɴᴛᴀx, ᴘʟᴇᴀꜱᴇ ᴄʜᴇᴄᴋ ʜᴇʟᴘ ᴍᴇɴᴜ ᴛᴏ ᴋɴᴏᴡ ᴍᴏʀᴇ ʙᴀʙʏ🥀!",
        )
        return
    pablo = await client.send_message(
        message.chat.id, f"`ɢᴇᴛᴛɪɴɢ {urlissed} ꜰʀᴏᴍ ʏᴏᴜᴛᴜʙᴇ ꜱᴇʀᴠᴇʀꜱ. ᴘʟᴇᴀꜱᴇ ᴡᴀɪᴛ ʙᴀʙʏ🥀.`"
    )
    search = SearchVideos(f"{urlissed}", offset=1, mode="dict", max_results=1)
    mi = search.result()
    mio = mi["search_result"]
    mo = mio[0]["link"]
    mio[0]["duration"]
    thum = mio[0]["title"]
    fridayz = mio[0]["id"]
    thums = mio[0]["channel"]
    kekme = f"https://img.youtube.com/vi/{fridayz}/hqdefault.jpg"
    await asyncio.sleep(0.6)
    sedlyf = wget.download(kekme)
    opts = {
        "format": "bestaudio",
        "addmetadata": True,
        "key": "FFmpegMetadata",
        "writethumbnail": True,
        "prefer_ffmpeg": True,
        "geo_bypass": True,
        "nocheckcertificate": True,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "720",
            }
        ],
        "outtmpl": "%(id)s.mp3",
        "quiet": True,
        "logtostderr": False,
    }
    try:
        with YoutubeDL(opts) as ytdl:
            ytdl_data = ytdl.extract_info(mo, download=True)
    except Exception as e:
        await pablo.edit(f"**ꜰᴀɪʟᴇᴅ ᴛᴏ ᴅᴏᴡɴʟᴏᴀᴅ** \n**ᴇʀʀᴏʀ :** `{str(e)}` ʙᴀʙʏ🥀")
        return
    c_time = time.time()
    capy = f"**Song Name :** [{thum}]({mo}) \n**Requested For :** `{urlissed}` \n**Channel :** `{thums}` "
    file_stark = f"{ytdl_data['id']}.mp3"
    await client.send_audio(
        message.chat.id,
        audio=open(file_stark, "rb"),
        duration=int(ytdl_data["duration"]),
        title=str(ytdl_data["title"]),
        performer=str(ytdl_data["uploader"]),
        thumb=sedlyf,
        caption=capy,
        progress=progress,
        progress_args=(
            pablo,
            c_time,
            f"`ᴜᴘʟᴏᴅɪɴɢ {urlissed} ꜱᴏɴɢ ꜰʀᴏᴍ ʏᴏᴜᴛᴜʙᴇ ᴍᴜꜱɪᴄ ʙᴀʙʏ🥀!`",
            file_stark,
        ),
    )
    await pablo.delete()
    for files in (sedlyf, file_stark):
        if files and os.path.exists(files):
            os.remove(files)
