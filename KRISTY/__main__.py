import html
import os
import asyncio
import json
import importlib
import time
import re
import sys
import traceback
import KRISTY.modules.sql.users_sql as sql
from sys import argv
from pyrogram import idle
from typing import Optional
from platform import python_version as memek
from KRISTY import (
    ALLOW_EXCL,
    CERT_PATH,
    OWNER_USERNAME,
    BOT_USERNAME as bu,
    LOGGER,
    OWNER_ID,
    PORT,
    SUPPORT_CHAT,
    TOKEN,
    URL,
    BOT_NAME,
    START_STICKER,
    START_IMG,
    UPDATES_CHANNEL,
    WEBHOOK,
    SUPPORT_CHAT,
    dispatcher,
    StartTime,
    telethn,
    pbot,
    updater,
)

# NOTE: Module order is not guaranteed, specify that in the config file!
from KRISTY.modules import ALL_MODULES
from KRISTY.modules.helper_funcs.chat_status import is_user_admin
from KRISTY.modules.helper_funcs.misc import paginate_modules
from telegram import __version__ as so
from pyrogram import __version__ as do
from telethon import __version__ as am
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode, Update
from telegram.error import (
    BadRequest,
    ChatMigrated,
    NetworkError,
    TelegramError,
    TimedOut,
    Unauthorized,
)
from telegram.ext import (
    CallbackContext,
    CallbackQueryHandler,
    CommandHandler,
    Filters,
    MessageHandler,
)
from telegram.ext.dispatcher import DispatcherHandlerStop, run_async
from telegram.utils.helpers import escape_markdown


def get_readable_time(seconds: int) -> str:
    count = 0
    ping_time = ""
    time_list = []
    time_suffix_list = ["s", "m", "h", "days"]

    while count < 4:
        count += 1
        remainder, result = divmod(seconds, 60) if count < 3 else divmod(seconds, 24)
        if seconds == 0 and remainder == 0:
            break
        time_list.append(int(result))
        seconds = int(remainder)

    for x in range(len(time_list)):
        time_list[x] = str(time_list[x]) + time_suffix_list[x]
    if len(time_list) == 4:
        ping_time += time_list.pop() + ", "

    time_list.reverse()
    ping_time += ":".join(time_list)

    return ping_time

DONATION_LINK = "https://t.me/Cute_arnavsingh"

start_txt = """
ʜᴇʏ🥀 `{}`, ʜᴏᴡ ᴀʀᴇ ʏᴏᴜ!!
"""

PM_START_TEXT = """
*Hello {} !*
» ɪ ᴀᴍ {} [🥀]({}) ᴀ ᴘᴏᴡᴇʀ ꜰᴜʟʟ ʙᴏᴛ ᴛᴏ ᴍᴀɴᴀɢᴇ ʏᴏᴜʀ ɢʀᴏᴜᴘꜱ
────────────────────────
» *Uptime:* `{}`
» `{}` *users, across* `{}` *chats.*
────────────────────────
» ʜɪᴛ /help ᴛᴏ ꜱᴇᴇ ᴍʏ ᴀᴠᴀɪʟᴀʙʟᴇ ᴄᴏᴍᴍᴀɴᴅꜱ.
"""

buttons = [
        [
        InlineKeyboardButton(
            text="ᴀᴅᴅ ᴍᴇ", url=f"t.me/{bu}?startgroup=true"
        )
    ],
    [
        InlineKeyboardButton(text="ᴄᴏᴍᴍᴀɴᴅꜱ", callback_data="help_back"),
    ],
    [
        InlineKeyboardButton(text="ᴀʙᴏᴜᴛ", callback_data="KRISTY_"),
        InlineKeyboardButton(text="ᴏᴡɴᴇʀ", url=f"https://t.me/{OWNER_USERNAME}"),
    ],
    [
        InlineKeyboardButton(text="sᴜᴘᴘᴏʀᴛ ", url=f"https://t.me/{SUPPORT_CHAT}"),
        InlineKeyboardButton(text="ᴜᴘᴅᴀᴛᴇs", url=f"https://t.me/{UPDATES_CHANNEL}"),
    ],
]


HELP_STRINGS = """
ᴄᴏᴍᴍᴀɴᴅs ᴀᴠᴀɪʟᴀʙʟᴇ:
» /help: PM's ʏᴏᴜ ᴛʜɪs ᴍᴇssᴀɢᴇ.
» /donate: ɪɴғᴏʀᴍᴀᴛɪᴏɴ ᴏɴ ʜᴏᴡ ᴛᴏ ᴅᴏɴᴀᴛᴇ!
» /settings:
   ↣ ɪɴ ᴘᴍ: ᴡɪʟʟ sᴇɴᴅ ʏᴏᴜ ʏᴏᴜʀ sᴇᴛᴛɪɴɢs ғᴏʀ ᴀʟʟ sᴜᴘᴘᴏʀᴛᴇᴅ ᴍᴏᴅᴜʟᴇs.
   ↣ ɪɴ ᴀ ɢʀᴏᴜᴘ: ᴡɪʟʟ ʀᴇᴅɪʀᴇᴄᴛ ʏᴏᴜ ᴛᴏ ᴘᴍ, ᴡɪᴛʜ ᴀʟʟ ᴛʜᴀᴛ ᴄʜᴀᴛ  sᴇᴛᴛɪɴɢs.
"""


DONATE_STRING = """ᴊᴜsᴛ sᴜᴘᴘᴏʀᴛ ᴜs"""


IMPORTED = {}
MIGRATEABLE = []
HELPABLE = {}
STATS = []
USER_INFO = []
DATA_IMPORT = []
DATA_EXPORT = []
CHAT_SETTINGS = {}
USER_SETTINGS = {}


for module_name in ALL_MODULES:
    imported_module = importlib.import_module(f"KRISTY.modules.{module_name}")
    if not hasattr(imported_module, "__mod_name__"):
        imported_module.__mod_name__ = imported_module.__name__

    if imported_module.__mod_name__.lower() not in IMPORTED:
        IMPORTED[imported_module.__mod_name__.lower()] = imported_module
    else:
        raise Exception("ᴄᴀɴ'ᴛ ʜᴀᴠᴇ ᴛᴡᴏ ᴍᴏᴅᴜʟᴇs ᴡɪᴛʜ ᴛʜᴇ sᴀᴍᴇ ɴᴀᴍᴇ! ᴘʟᴇᴀsᴇ ᴄʜᴀɴɢᴇ ᴏɴᴇ")

    if hasattr(imported_module, "__help__") and imported_module.__help__:
        HELPABLE[imported_module.__mod_name__.lower()] = imported_module

    # Chats to migrate on chat_migrated events
    if hasattr(imported_module, "__migrate__"):
        MIGRATEABLE.append(imported_module)

    if hasattr(imported_module, "__stats__"):
        STATS.append(imported_module)

    if hasattr(imported_module, "__user_info__"):
        USER_INFO.append(imported_module)

    if hasattr(imported_module, "__import_data__"):
        DATA_IMPORT.append(imported_module)

    if hasattr(imported_module, "__export_data__"):
        DATA_EXPORT.append(imported_module)

    if hasattr(imported_module, "__chat_settings__"):
        CHAT_SETTINGS[imported_module.__mod_name__.lower()] = imported_module

    if hasattr(imported_module, "__user_settings__"):
        USER_SETTINGS[imported_module.__mod_name__.lower()] = imported_module


# do not async
def send_help(chat_id, text, keyboard=None):
    if not keyboard:
        keyboard = InlineKeyboardMarkup(paginate_modules(0, HELPABLE, "help"))
    dispatcher.bot.send_message(
        chat_id=chat_id,
        text=text,
        parse_mode=ParseMode.MARKDOWN,
        disable_web_page_preview=True,
        reply_markup=keyboard,
    )


def test(update: Update, context: CallbackContext):
    # pprint(eval(str(update)))
    # update.effective_message.reply_text("Hola tester! _I_ *have* `markdown`", parse_mode=ParseMode.MARKDOWN)
    update.effective_message.reply_text("ᴛʜɪs ᴘᴇʀsᴏɴ ᴇᴅɪᴛᴇᴅ ᴀ ᴍᴇssᴀɢᴇ")
    print(update.effective_message)


def start(update: Update, context: CallbackContext):
    args = context.args
    usr = update.effective_user
    uptime = get_readable_time((time.time() - StartTime))
    if update.effective_chat.type == "private":
        if len(args) >= 1:
            if args[0].lower() == "help":
                send_help(update.effective_chat.id, HELP_STRINGS)
            elif args[0].lower().startswith("ghelp_"):
                mod = args[0].lower().split("_", 1)[1]
                if mod == "Admins":
                    mod = "Admins"
                if not HELPABLE.get(mod, False):
                    return
                send_help(
                    update.effective_chat.id,
                    HELPABLE[mod].__help__,
                    InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton(
                                    text="ʙᴀᴄᴋ", callback_data="help_back"
                                )
                            ]
                        ]
                    ),
                )

            elif args[0].lower().startswith("stngs_"):
                match = re.match("stngs_(.*)", args[0].lower())
                chat = dispatcher.bot.getChat(match[1])

                if is_user_admin(chat, update.effective_user.id):
                    send_settings(match[1], update.effective_user.id, False)
                else:
                    send_settings(match[1], update.effective_user.id, True)

            elif args[0][1:].isdigit() and "rules" in IMPORTED:
                IMPORTED["rules"].send_rules(update, args[0], from_pm=True)

        else:
            first_name = update.effective_user.first_name
            lel = update.effective_message.reply_text(
                start_txt.format(usr.first_name), parse_mode=ParseMode.MARKDOWN
            )
            time.sleep(1.2)
            lel.edit_text(f"ᴡᴀɪᴛ ʙᴀʙʏ🖤! ʟᴇᴛ ᴍᴇ ɢᴇᴛ ꜱᴛᴀʀᴛᴇᴅ \nꜱᴏ ᴛʜᴀᴛ ʏᴏᴜ ᴄᴀɴ ᴜꜱᴇ ᴍʏ ᴘᴏᴡᴇʀ🤌❤️")
            time.sleep(1.2)
            lel.delete()
            K = update.effective_message.reply_sticker(
                f"{START_STICKER}"
            )
            time.sleep(1.2)
            K.delete()
            update.effective_message.reply_text(
                PM_START_TEXT.format(
                    escape_markdown(first_name),
                    escape_markdown(BOT_NAME),
                    escape_markdown(START_IMG),
                    escape_markdown(uptime),
                    sql.num_users(),
                    sql.num_chats(),
                ),
                reply_markup=InlineKeyboardMarkup(buttons),
                parse_mode=ParseMode.MARKDOWN,
                timeout=60,
                disable_web_page_preview=False,
            )
    else:
        update.effective_message.reply_photo(
            START_IMG,
            caption="ʜᴇʏ `{}`,\n\nɪ ᴀᴍ ᴀʟɪᴠᴇ ʙᴀʙʏ🖤!\n➥ᴜᴘᴛɪᴍᴇ: `{}` \n➥ᴜsᴇʀs: `{}` \n➥ᴄʜᴀᴛs: `{}` ".format(
                usr.first_name,
                uptime,
                sql.num_users(),
                sql.num_chats(),
            ),
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="ʜᴇʟᴘ",
                            url=f"https://t.me/{bu}?start=help",
                        ),
                        InlineKeyboardButton(
                            text="ᴏᴡɴᴇʀ",
                            url=f"https://t.me/{OWNER_USERNAME}",
                        ),
                    ],
                ]
            ),
        )


def error_handler(update, context):
    """Log the error and send a telegram message to notify the developer."""
    # Log the error before we do anything else, so we can see it even if something breaks.
    LOGGER.error(msg="Exception while handling an update:", exc_info=context.error)

    # traceback.format_exception returns the usual python message about an exception, but as a
    # list of strings rather than a single string, so we have to join them together.
    tb_list = traceback.format_exception(
        None, context.error, context.error.__traceback__
    )
    tb = "".join(tb_list)

    # Build the message with some markup and additional information about what happened.
    message = (
        "An exception was raised while handling an update\n"
        "<pre>update = {}</pre>\n\n"
        "<pre>{}</pre>"
    ).format(
        html.escape(json.dumps(update.to_dict(), indent=2, ensure_ascii=False)),
        html.escape(tb),
    )

    if len(message) >= 4096:
        message = message[:4096]
    # Finally, send the message
    context.bot.send_message(chat_id=OWNER_ID, text=message, parse_mode=ParseMode.HTML)


# for test purposes
def error_callback(update: Update, context: CallbackContext):
    error = context.error
    try:
        raise error
    except Unauthorized:
        print("no nono1")
        print(error)
        # remove update.message.chat_id from conversation list
    except BadRequest:
        print("no nono2")
        print("BadRequest caught")
        print(error)

        # handle malformed requests - read more below!
    except TimedOut:
        print("no nono3")
        # handle slow connection problems
    except NetworkError:
        print("no nono4")
        # handle other connection problems
    except ChatMigrated as err:
        print("no nono5")
        print(err)
        # the chat_id of a group has changed, use e.new_chat_id instead
    except TelegramError:
        print(error)
        # handle all other telegram related errors


def help_button(update, context):
    query = update.callback_query
    mod_match = re.match(r"help_module\((.+?)\)", query.data)
    prev_match = re.match(r"help_prev\((.+?)\)", query.data)
    next_match = re.match(r"help_next\((.+?)\)", query.data)
    back_match = re.match(r"help_back", query.data)

    print(query.message.chat.id)

    try:
        if mod_match:
            module = mod_match.group(1)
            text = (
                "ʜᴇʀᴇ ɪꜱ ᴛʜᴇ ʜᴇʟᴘ ꜰᴏʀ ᴛʜᴇ *{}* ᴍᴏᴅᴜʟᴇ:\n".format(
                    HELPABLE[module].__mod_name__
                )
                + HELPABLE[module].__help__
            )
            query.message.edit_text(
                text=text,
                parse_mode=ParseMode.MARKDOWN,
                disable_web_page_preview=True,
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton(text="◁", callback_data="help_back")]]
                ),
            )

        elif prev_match:
            curr_page = int(prev_match.group(1))
            query.message.edit_text(
                text=HELP_STRINGS,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(curr_page - 1, HELPABLE, "help")
                ),
            )

        elif next_match:
            next_page = int(next_match.group(1))
            query.message.edit_text(
                text=HELP_STRINGS,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(next_page + 1, HELPABLE, "help")
                ),
            )

        elif back_match:
            query.message.edit_text(
                text=HELP_STRINGS,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(0, HELPABLE, "help")
                ),
            )

        # ensure no spinny white circle
        context.bot.answer_callback_query(query.id)
        # query.message.delete()

    except BadRequest:
        pass


def KRISTY_about_callback(update, context):
    query = update.callback_query
    if query.data == "KRISTY_":
        query.message.edit_text(
            text=f"๏ I'm [{BOT_NAME}](https://t.me/Miss_Kristy_robot), ᴀ ᴘᴏᴡᴇʀꜰᴜʟ ɢʀᴏᴜᴘ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ ʙᴏᴛ ʙᴜɪʟᴛ ᴛᴏ ʜᴇʟᴘ ʏᴏᴜ ᴍᴀɴᴀɢᴇ ʏᴏᴜʀ ɢʀᴏᴜᴘ ᴇᴀꜱɪʟʏ."
            "\n» ɪ ᴄᴀɴ ʀᴇꜱᴛʀɪᴄᴛ ᴜꜱᴇʀꜱ."
            "\n» ɪ ᴀᴍ ʙᴜɪʟᴛ ᴡɪᴛʜ [ᴘʏᴛʜᴏɴ](https://www.python.org/) ,[ᴍᴏɴɢᴏᴅʙ](https://www.mongodb.com/)."
            "\n» ᴍʏ ʙᴀꜱᴇ ɪꜱ ᴍᴀᴅᴇ ᴜᴘ ᴏꜰ [ᴛᴇʟᴇᴛʜᴏɴ](https://github.com/LonamiWebs/Telethon) ᴀɴᴅ [ᴘʏʀᴏɢʀᴀᴍ](https://github.com/pyrogram/pyrogram)."
            "\n» ɪ ʜᴀᴠᴇ ᴀɴ ᴀᴅᴠᴀɴᴄᴇᴅ ᴀɴᴛɪ-ꜰʟᴏᴏᴅ ꜱʏꜱᴛᴇᴍ."
            "\n» ɪ ʜᴀᴠᴇ ɴꜱᴡꜰ ᴛᴏ ᴅᴇᴛᴇᴄᴛ ᴀᴅᴜʟᴛ ᴄᴏɴᴛᴇɴᴛꜱ ᴀɴᴅ ᴛᴏ ᴘʀᴏᴛᴇᴄᴛ ᴛʜᴇ ɢʀᴏᴜᴘ ꜰʀᴏᴍ ᴘᴏʀɴᴏɢʀᴀᴘʜɪᴄ ᴄᴏɴᴛᴇɴᴛꜱ."
            "\n» ɪ ᴄᴀɴ ᴘʀᴏᴛᴇᴄᴛ ʏᴏᴜʀ ɢʀᴏᴜᴘ ꜰʀᴏᴍ ꜱᴘᴀᴍꜱ ᴀɴᴅ ʀᴀɪᴅꜱ."
            "\n» ɪ ʜᴀᴠᴇ ᴍᴀɴʏ ᴛᴏᴏʟꜱ ꜰᴏʀ ꜰᴜɴ ᴀɴᴅ ᴇɴᴊᴏʏᴍᴇɴᴛ ᴛᴏ ᴇɴᴛᴇʀᴛᴀɪɴ ʏᴏᴜ ᴀʟʟ"
            "\n» ɪ ᴀᴍ ᴘᴜʙʟɪꜱʜᴇᴅ ᴜɴᴅᴇʀ ʟɪᴄᴇɴꜱᴇ :- [ɢɴᴜ ʟɪᴄᴇɴꜱᴇ](https://github.com/Xdarnav/ArnavXMusic/blob/main/LICENSE)"
            "\n\n 𝗧𝗛𝗔𝗡𝗞𝗦 𝗙𝗢𝗥 𝗦𝗨𝗣𝗣𝗢𝗥𝗧𝗜𝗡𝗚 𝗨𝗦",
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [
                 [
        InlineKeyboardButton(text="ᴏᴡɴᴇʀ", url=f"https://t.me/{OWNER_USERNAME}"),
        InlineKeyboardButton(text="ᴅᴇᴠᴇʟᴏᴘᴇʀ", url=f"https://t.me/Cute_arnavsingh"),
                 ],
                 [
        InlineKeyboardButton(text="ꜱᴏᴜʀᴄᴇ", url=f"https://github.com/Xdarnav/ArnavXMusic"),
                 ],
                 [
                    InlineKeyboardButton(text="◁", callback_data="KRISTY_back"),
                 ]
                ]
            ),
        )


    elif query.data == "KRISTY_back":
        first_name = update.effective_user.first_name
        uptime = get_readable_time((time.time() - StartTime))
        query.message.edit_text(
                PM_START_TEXT.format(
                    escape_markdown(first_name),
                    escape_markdown(BOT_NAME),
                    escape_markdown(START_IMG),
                    escape_markdown(uptime),
                    sql.num_users(),
                    sql.num_chats(),
                ),
            reply_markup=InlineKeyboardMarkup(buttons),
            parse_mode=ParseMode.MARKDOWN,
            timeout=60,
            disable_web_page_preview=False,
        )


def Source_about_callback(update, context):
    query = update.callback_query
    if query.data == "source_":
        query.message.edit_text(
            text="๏›› soon",
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [
                 [
                    InlineKeyboardButton(text="◁", callback_data="KRISTY_")
                 ]
                ]
            ),
        )
    elif query.data == "source_back":
        first_name = update.effective_user.first_name
        query.message.edit_text(
                                PM_START_TEXT.format(
                    escape_markdown(first_name),
                    escape_markdown(BOT_NAME),
                    escape_markdown(START_IMG),
                    escape_markdown(uptime),
                    sql.num_users(),
                    sql.num_chats(),
                ),
                reply_markup=InlineKeyboardMarkup(buttons),
                parse_mode=ParseMode.MARKDOWN,
                timeout=60,
                disable_web_page_preview=False,
        )

def get_help(update: Update, context: CallbackContext):
    chat = update.effective_chat  # type: Optional[Chat]
    args = update.effective_message.text.split(None, 1)

    # ONLY send help in PM
    if chat.type != chat.PRIVATE:
        if len(args) >= 2 and any(args[1].lower() == x for x in HELPABLE):
            module = args[1].lower()
            update.effective_message.reply_text(
                f"ᴄᴏɴᴛᴀᴄᴛ ᴍᴇ ɪɴ ᴘᴍ ᴛᴏ ɢᴇᴛ ʜᴇʟᴘ ᴏꜰ {module.capitalize()}",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                text="ʜᴇʟᴘ",
                                url="t.me/{}?start=ghelp_{}".format(
                                    context.bot.username, module
                                ),
                            )
                        ]
                    ]
                ),
            )
            return
        update.effective_message.reply_text(
            "ᴄᴏɴᴛᴀᴄᴛ ᴍᴇ ɪɴ ᴘᴍ ᴛᴏ ɢᴇᴛ ᴛʜᴇ ʟɪꜱᴛ ᴏꜰ ᴘᴏꜱꜱɪʙʟᴇ ᴄᴏᴍᴍᴀɴᴅꜱ.",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="ʜᴇʟᴘ",
                            url="t.me/{}?start=help".format(context.bot.username),
                        )
                    ]
                ]
            ),
        )
        return

    elif len(args) >= 2 and any(args[1].lower() == x for x in HELPABLE):
        module = args[1].lower()
        text = (
            "ʜᴇʀᴇ ɪꜱ ᴛʜᴇ ᴀᴠᴀɪʟᴀʙʟᴇ ʜᴇʟᴘ ꜰᴏʀ ᴛʜᴇ *{}* ᴍᴏᴅᴜʟᴇ:\n".format(
                HELPABLE[module].__mod_name__
            )
            + HELPABLE[module].__help__
        )
        send_help(
            chat.id,
            text,
            InlineKeyboardMarkup(
                [[InlineKeyboardButton(text="◁", callback_data="help_back")]]
            ),
        )

    else:
        send_help(chat.id, HELP_STRINGS)


def send_settings(chat_id, user_id, user=False):
    if user:
        if USER_SETTINGS:
            settings = "\n\n".join(
                "*{}*:\n{}".format(mod.__mod_name__, mod.__user_settings__(user_id))
                for mod in USER_SETTINGS.values()
            )
            dispatcher.bot.send_message(
                user_id,
                "ᴛʜᴇꜱᴇ ᴀʀᴇ ʏᴏᴜʀ ᴄᴜʀʀᴇɴᴛ ꜱᴇᴛᴛɪɴɢꜱ:" + "\n\n" + settings,
                parse_mode=ParseMode.MARKDOWN,
            )

        else:
            dispatcher.bot.send_message(
                user_id,
                "ꜱᴇᴇᴍꜱ ʟɪᴋᴇ ᴛʜᴇʀᴇ ᴀʀᴇɴ'ᴛ ᴀɴʏ ᴜꜱᴇʀ ꜱᴘᴇᴄɪꜰɪᴄ ꜱᴇᴛᴛɪɴɢꜱ ᴀᴠᴀɪʟᴀʙʟᴇ :'(",
                parse_mode=ParseMode.MARKDOWN,
            )

    else:
        if CHAT_SETTINGS:
            chat_name = dispatcher.bot.getChat(chat_id).title
            dispatcher.bot.send_message(
                user_id,
                text="ᴡʜɪᴄʜ ᴍᴏᴅᴜʟᴇ ᴡᴏᴜʟᴅ ʏᴏᴜ ʟɪᴋᴇ ᴛᴏ ᴄʜᴇᴄᴋ {}'ꜱ ꜱᴇᴛᴛɪɴɢꜱ ꜰᴏʀ?".format(
                    chat_name
                ),
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(0, CHAT_SETTINGS, "stngs", chat=chat_id)
                ),
            )
        else:
            dispatcher.bot.send_message(
                user_id,
                "ꜱᴇᴇᴍꜱ ʟɪᴋᴇ ᴛʜᴇʀᴇ ᴀʀᴇɴ'ᴛ ᴀɴʏ ᴄʜᴀᴛ ꜱᴇᴛᴛɪɴɢꜱ ᴀᴠᴀɪʟᴀʙʟᴇ :'(\nꜱᴇɴᴅ ᴛʜɪꜱ "
                "ɪɴ ᴀ ɢʀᴏᴜᴘ ᴄʜᴀᴛ ʏᴏᴜ'ʀᴇ ᴀᴅᴍɪɴ ɪɴ ᴛᴏ ꜰɪɴᴅ ɪᴛꜱ ᴄᴜʀʀᴇɴᴛ ꜱᴇᴛᴛɪɴɢꜱ!",
                parse_mode=ParseMode.MARKDOWN,
            )


def settings_button(update: Update, context: CallbackContext):
    query = update.callback_query
    user = update.effective_user
    bot = context.bot
    mod_match = re.match(r"stngs_module\((.+?),(.+?)\)", query.data)
    prev_match = re.match(r"stngs_prev\((.+?),(.+?)\)", query.data)
    next_match = re.match(r"stngs_next\((.+?),(.+?)\)", query.data)
    back_match = re.match(r"stngs_back\((.+?)\)", query.data)
    try:
        if mod_match:
            chat_id = mod_match.group(1)
            module = mod_match.group(2)
            chat = bot.get_chat(chat_id)
            text = "*{}* ʜᴀꜱ ᴛʜᴇ ꜰᴏʟʟᴏᴡɪɴɢ ꜱᴇᴛᴛɪɴɢꜱ ꜰᴏʀ ᴛʜᴇ *{}* ᴍᴏᴅᴜʟᴇ:\n\n".format(
                escape_markdown(chat.title), CHAT_SETTINGS[module].__mod_name__
            ) + CHAT_SETTINGS[module].__chat_settings__(chat_id, user.id)
            query.message.reply_text(
                text=text,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                text="◁",
                                callback_data="stngs_back({})".format(chat_id),
                            )
                        ]
                    ]
                ),
            )

        elif prev_match:
            chat_id = prev_match.group(1)
            curr_page = int(prev_match.group(2))
            chat = bot.get_chat(chat_id)
            query.message.reply_text(
        "ʜɪ ᴛʜᴇʀᴇ! ᴛʜᴇʀᴇ ᴀʀᴇ Qᴜɪᴛᴇ ᴀ ꜰᴇᴡ ꜱᴇᴛᴛɪɴɢꜱ ꜰᴏʀ {} - ɢᴏ ᴀʜᴇᴀᴅ ᴀɴᴅ ᴘɪᴄᴋ ᴡʜᴀᴛ "
                "ʏᴏᴜ'ʀᴇ ɪɴᴛᴇʀᴇꜱᴛᴇᴅ ɪɴ.".format(chat.title),
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(
                        curr_page - 1, CHAT_SETTINGS, "stngs", chat=chat_id
                    )
                ),
            )

        elif next_match:
            chat_id = next_match.group(1)
            next_page = int(next_match.group(2))
            chat = bot.get_chat(chat_id)
            query.message.reply_text(
                "ʜɪ ᴛʜᴇʀᴇ! ᴛʜᴇʀᴇ ᴀʀᴇ Qᴜɪᴛᴇ ᴀ ꜰᴇᴡ ꜱᴇᴛᴛɪɴɢꜱ ꜰᴏʀ {} - ɢᴏ ᴀʜᴇᴀᴅ ᴀɴᴅ ᴘɪᴄᴋ ᴡʜᴀᴛ "
                "ʏᴏᴜ'ʀᴇ ɪɴᴛᴇʀᴇꜱᴛᴇᴅ ɪɴ.".format(chat.title),
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(
                        next_page + 1, CHAT_SETTINGS, "stngs", chat=chat_id
                    )
                ),
            )

        elif back_match:
            chat_id = back_match.group(1)
            chat = bot.get_chat(chat_id)
            query.message.reply_text(
                text="ʜɪ ᴛʜᴇʀᴇ! ᴛʜᴇʀᴇ ᴀʀᴇ Qᴜɪᴛᴇ ᴀ ꜰᴇᴡ ꜱᴇᴛᴛɪɴɢꜱ ꜰᴏʀ {} - ɢᴏ ᴀʜᴇᴀᴅ ᴀɴᴅ ᴘɪᴄᴋ ᴡʜᴀᴛ "
                "ʏᴏᴜ'ʀᴇ ɪɴᴛᴇʀᴇꜱᴛᴇᴅ ɪɴ.".format(escape_markdown(chat.title)),
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(0, CHAT_SETTINGS, "stngs", chat=chat_id)
                ),
            )

        # ensure no spinny white circle
        bot.answer_callback_query(query.id)
        query.message.delete()
    except BadRequest as excp:
        if excp.message not in [
            "ᴍᴇꜱꜱᴀɢᴇ ɪꜱ ɴᴏᴛ ᴍᴏᴅɪꜰɪᴇᴅ",
            "Qᴜᴇʀʏ_ɪᴅ_ɪɴᴠᴀʟɪᴅ",
            "ᴍᴇꜱꜱᴀɢᴇ ᴄᴀɴ'ᴛ ʙᴇ ᴅᴇʟᴇᴛᴇᴅ",
        ]:
            LOGGER.exception("ᴇxᴄᴇᴘᴛɪᴏɴ ɪɴ ꜱᴇᴛᴛɪɴɢꜱ ʙᴜᴛᴛᴏɴꜱ. %s", str(query.data))


def get_settings(update: Update, context: CallbackContext):
    chat = update.effective_chat  # type: Optional[Chat]
    user = update.effective_user  # type: Optional[User]
    msg = update.effective_message  # type: Optional[Message]

    # ONLY send settings in PM
    if chat.type != chat.PRIVATE:
        if is_user_admin(chat, user.id):
            text = "ᴄʟɪᴄᴋ ʜᴇʀᴇ ᴛᴏ ɢᴇᴛ ᴛʜɪꜱ ᴄʜᴀᴛ'ꜱ ꜱᴇᴛᴛɪɴɢꜱ, ᴀꜱ ᴡᴇʟʟ ᴀꜱ ʏᴏᴜʀꜱ."
            msg.reply_text(
                text,
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                text="ꜱᴇᴛᴛɪɴɢꜱ",
                                url="t.me/{}?start=stngs_{}".format(
                                    context.bot.username, chat.id
                                ),
                            )
                        ]
                    ]
                ),
            )
        else:
            text = "ᴄʟɪᴄᴋ ʜᴇʀᴇ ᴛᴏ ᴄʜᴇᴄᴋ ʏᴏᴜʀ ꜱᴇᴛᴛɪɴɢꜱ."

    else:
        send_settings(chat.id, user.id, True)


def donate(update: Update, context: CallbackContext):
    user = update.effective_message.from_user
    chat = update.effective_chat  # type: Optional[Chat]
    bot = context.bot
    if chat.type == "private":
        update.effective_message.reply_text(
            DONATE_STRING, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True
        )

        if OWNER_ID != 5482561033:
            update.effective_message.reply_text(
                "ɪ'ᴍ ꜰʀᴇᴇ ꜰᴏʀ ᴇᴠᴇʀʏᴏɴᴇ 🖤 ɪꜰ ʏᴏᴜ ᴡᴀɴɴᴀ ᴍᴀᴋᴇ ᴍᴇ ꜱᴍɪʟᴇ, ᴊᴜꜱᴛ ᴊᴏɪɴ"
                "[My Channel]({})".format(DONATION_LINK),
                parse_mode=ParseMode.MARKDOWN,
            )
    else:
        try:
            bot.send_message(
                user.id,
                DONATE_STRING,
                parse_mode=ParseMode.MARKDOWN,
                disable_web_page_preview=True,
            )

            update.effective_message.reply_text(
                "ɪ'ᴠᴇ ᴘᴍ'ᴇᴅ ʏᴏᴜ ᴀʙᴏᴜᴛ ᴅᴏɴᴀᴛɪɴɢ ᴛᴏ ᴍʏ ᴄʀᴇᴀᴛᴏʀ!"
            )
        except Unauthorized:
            update.effective_message.reply_text(
                "ᴄᴏɴᴛᴀᴄᴛ ᴍᴇ ɪɴ ᴘᴍ ꜰɪʀꜱᴛ ᴛᴏ ɢᴇᴛ ᴅᴏɴᴀᴛɪᴏɴ ɪɴꜰᴏʀᴍᴀᴛɪᴏɴ."
            )


def migrate_chats(update: Update, context: CallbackContext):
    msg = update.effective_message  # type: Optional[Message]
    if msg.migrate_to_chat_id:
        old_chat = update.effective_chat.id
        new_chat = msg.migrate_to_chat_id
    elif msg.migrate_from_chat_id:
        old_chat = msg.migrate_from_chat_id
        new_chat = update.effective_chat.id
    else:
        return

    LOGGER.info("ᴍɪɢʀᴀᴛɪɴɢ ꜰʀᴏᴍ %s, to %s", str(old_chat), str(new_chat))
    for mod in MIGRATEABLE:
        mod.__migrate__(old_chat, new_chat)

    LOGGER.info("ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ ᴍɪɢʀᴀᴛᴇᴅ!")
    raise DispatcherHandlerStop


def main():

    if SUPPORT_CHAT is not None and isinstance(SUPPORT_CHAT, str):
        try:
            dispatcher.bot.sendAnimation(
                f"@{SUPPORT_CHAT}",
                animation="https://te.legra.ph/file/90435295a1858b0c03c76.mp4",
                caption=f"""
ㅤ{dispatcher.bot.first_name} ɪs ᴀʟɪᴠᴇ ʙᴀʙʏ .....
━━━━━━━━━━━━━
» **ᴏᴡɴᴇʀ :** [𓄂➖⃟🥀𓆩👑𝗔ʀɴᴀᴠ🥀⃝➻𝐒ɪɴɢʜ👑𓆪⁩💗 ̶⧉⃞ ⃝⃪⃜🕊️](https://t.me/{OWNER_USERNAME})
» **ʟɪʙʀᴀʀʏ  :** `{so}`
» **ᴛᴇʟᴇᴛʜᴏɴ :** `{am}`
» **ᴘʏʀᴏɢʀᴀᴍ :** `{do}`
» **ᴍᴏɴɢᴏ ᴅʙ :** `3.9.0`
» **ꜱQʟᴀʟᴄʜᴇᴍʏ :** `1.4.31`
━━━━━━━━━━━━━

⍟ ᴘᴏᴡᴇʀᴇᴅ ʙʏ : [𝗶𝗹𝗲𝘅𝘄𝗼𝗿𝗹𝗱](https://t.me/link_copied)

""",
                parse_mode=ParseMode.MARKDOWN,
            )
        except Unauthorized:
            LOGGER.warning(
                "ʙᴏᴛ ɪsɴᴛ ᴀʙʟᴇ ᴛᴏ sᴇɴᴅ ᴍᴇssᴀɢᴇ ᴛᴏ support_chat, ɢᴏ ᴀɴᴅ ᴄʜᴇᴄᴋ !"
            )
        except BadRequest as e:
            LOGGER.warning(e.message)

    test_handler = CommandHandler("test", test, run_async=True)
    start_handler = CommandHandler("start", start, run_async=True)

    help_handler = CommandHandler("help", get_help, run_async=True)
    help_callback_handler = CallbackQueryHandler(
        help_button, pattern=r"help_.*", run_async=True
    )

    settings_handler = CommandHandler("settings", get_settings, run_async=True)
    settings_callback_handler = CallbackQueryHandler(
        settings_button, pattern=r"stngs_", run_async=True
    )

    about_callback_handler = CallbackQueryHandler(
        KRISTY_about_callback, pattern=r"KRISTY_", run_async=True
    )

    source_callback_handler = CallbackQueryHandler(
        Source_about_callback, pattern=r"source_", run_async=True
    )

    donate_handler = CommandHandler("donate", donate, run_async=True)
    migrate_handler = MessageHandler(
        Filters.status_update.migrate, migrate_chats, run_async=True
    )

    dispatcher.add_handler(test_handler)
    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(help_handler)
    dispatcher.add_handler(about_callback_handler)
    dispatcher.add_handler(source_callback_handler)
    dispatcher.add_handler(settings_handler)
    dispatcher.add_handler(help_callback_handler)
    dispatcher.add_handler(settings_callback_handler)
    dispatcher.add_handler(migrate_handler)
    dispatcher.add_handler(donate_handler)

    dispatcher.add_error_handler(error_callback)

    if WEBHOOK:
        LOGGER.info("ᴜsɪɴɢ webhooks.")
        updater.start_webhook(listen="0.0.0.0", port=PORT, url_path=TOKEN)

        if CERT_PATH:
            updater.bot.set_webhook(url=URL + TOKEN, certificate=open(CERT_PATH, "rb"))
        else:
            updater.bot.set_webhook(url=URL + TOKEN)

    else:
        LOGGER.info(f"{BOT_NAME} STARTED, USING LONG POLLING. | SUPPORT: [@{SUPPORT_CHAT}]")
        updater.start_polling(
            timeout=15,
            read_latency=4,
            drop_pending_updates=True,
            allowed_updates=Update.ALL_TYPES,
        )


if __name__ == "__main__":
    LOGGER.info(
        f"BOT STARTED SUCCESSFULLY IF YOU FACE ANY ISSUE THEN JOIN @link_copied : {str(ALL_MODULES)}"
    )
    telethn.start(bot_token=TOKEN)
    pbot.start()
    main()
    idle()
