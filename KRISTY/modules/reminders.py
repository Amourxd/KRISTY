import re
import time

from telegram import Update
from telegram.ext import CommandHandler, run_async
from telegram.ext.callbackcontext import CallbackContext
from telegram.ext.filters import Filters
from telegram.parsemode import ParseMode

from KRISTY import OWNER_ID, updater, dispatcher
from KRISTY.modules.disable import DisableAbleCommandHandler


job_queue = updater.job_queue


def get_time(time: str) -> int:
    if time[-1] == "s":
        return int(time[:-1])
    if time[-1] == "m":
        return int(time[:-1])*60
    if time[-1] == "h":
        return int(time[:-1])*3600
    if time[-1] == "d":
        return int(time[:-1])*86400



reminder_message = """
ʏᴏᴜʀ ʀᴇᴍɪɴᴅᴇʀ:
{reason}
<i>ᴡʜɪᴄʜ ʏᴏᴜ ᴛɪᴍᴇᴅ {time} ʙᴇꜰᴏʀᴇ ɪɴ {title} ʙᴀʙʏ🥀</i>
"""

def reminders(update: Update, context: CallbackContext):
    user = update.effective_user
    msg = update.effective_message
    jobs = list(job_queue.jobs())
    user_reminders = []
    for job in jobs:
        if job.name.endswith(str(user.id)):
            user_reminders.append(job.name[1:])
    if len(user_reminders) == 0:
        msg.reply_text(
            text = "ʏᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴀɴʏ ʀᴇᴍɪɴᴅᴇʀꜱ ꜱᴇᴛ ᴏʀ ᴀʟʟ ᴛʜᴇ ʀᴇᴍɪɴᴅᴇʀꜱ ʏᴏᴜ ʜᴀᴠᴇ ꜱᴇᴛ ʜᴀᴠᴇ ʙᴇᴇɴ ᴄᴏᴍᴘʟᴇᴛᴇᴅ ʙᴀʙʏ🥀",
            reply_to_message_id = msg.message_id
        )
        return
    reply_text = "ʏᴏᴜʀ ʀᴇᴍɪɴᴅᴇʀꜱ (<i>ᴍᴇɴᴛɪᴏɴᴇᴅ ʙᴇʟᴏᴡ ᴀʀᴇ ᴛʜᴇ <b>ᴛɪᴍꜱᴛᴀᴍᴘꜱ</b> ᴏꜰ ᴛʜᴇ ʀᴇᴍɪɴᴅᴇʀꜱ ʏᴏᴜ ʜᴀᴠᴇ ꜱᴇᴛ </i>):\n"
    for i, u in enumerate(user_reminders):
        reply_text += f"\n{i+1}. <code>{u}</code>"
    msg.reply_text(
        text = reply_text,
        reply_to_message_id = msg.message_id,
        parse_mode = ParseMode.HTML
    )


def set_reminder(update: Update, context: CallbackContext):
    user = update.effective_user
    msg = update.effective_message
    chat = update.effective_chat
    reason = msg.text.split()
    if len(reason) == 1:
        msg.reply_text(
            "ɴᴏ ᴛɪᴍᴇ ᴀɴᴅ ʀᴇᴍɪɴᴅᴇʀ ᴛᴏ ᴍᴇɴᴛɪᴏɴ ʙᴀʙʏ🥀!",
            reply_to_message_id = msg.message_id
        )
        return
    if len(reason) == 2:
        msg.reply_text(
            "ɴᴏᴛʜɪɴɢ ᴛᴏ ʀᴇᴍɪɴᴅᴇʀ! ᴀᴅᴅ ᴀ ʀᴇᴍɪɴᴅᴇʀ ʙᴀʙʏ🥀",
            reply_to_message_id = msg.message_id
        )
        return
    t = reason[1].lower()
    if not re.match(r'[0-9]+(d|h|m|s)', t):
        msg.reply_text(
            "ᴜꜱᴇ ᴀ ᴄᴏʀʀᴇᴄᴛ ꜰᴏʀᴍᴀᴛ ᴏꜰ ᴛɪᴍᴇ ʙᴀʙʏ🥀!",
            reply_to_message_id = msg.message_id
        )
        return
    def job(context: CallbackContext):
        title = ""
        if chat.type == "private": title += "this chat"
        if chat.type != "private": title += chat.title
        context.bot.send_message(
            chat_id = user.id,
            text = reminder_message.format(
                reason = " ".join(reason[2:]),
                time = t,
                title = title
            ),
            disable_notification = False,
            parse_mode = ParseMode.HTML
        )
    job_time = time.time()
    job_queue.run_once(
        callback = job, 
        when = get_time(t), 
        name = f"t{job_time}{user.id}".replace(".", "")
    )
    msg.reply_text(
        text = f"ʏᴏᴜʀ ʀᴇᴍɪɴᴅᴇʀ ʜᴀꜱ ʙᴇᴇɴ ꜱᴇᴛ ᴀꜰᴛᴇʀ {time} ꜰʀᴏᴍ ɴᴏᴡ ʙᴀʙʏ🥀".format(
            time = t,
            time_stamp = str(job_time).replace(".", "") + str(user.id)
        ), 
        reply_to_message_id = msg.message_id,
        parse_mode = ParseMode.HTML
    )
    
def clear_reminder(update: Update, context: CallbackContext):
    user = update.effective_user
    msg = update.effective_message
    text = msg.text.split()
    if len(text) == 1 or not re.match(r'[0-9]+', text[1]):
        msg.reply_text(
            text = "ɴᴏ/ᴡʀᴏɴɢ ᴛɪᴍᴇꜱᴛᴀᴍᴘ ᴍᴇɴᴛɪᴏɴᴇᴅ ʙᴀʙʏ🥀",
            reply_to_message_id = msg.message_id
        )
        return
    if not text[1].endswith(str(user.id)):
        msg.reply_text(
            text = "ᴛʜᴇ ᴛɪᴍᴇꜱᴛᴀᴍᴘ ᴍᴇɴᴛɪᴏɴᴇᴅ ɪꜱ ɴᴏᴛ ʏᴏᴜʀ ʀᴇᴍɪɴᴅᴇʀ ʙᴀʙʏ🥀!",
            reply_to_message_id = msg.message_id
        )
        return
    jobs = list(job_queue.get_jobs_by_name("t" + text[1]))
    if len(jobs) == 0:
        msg.reply_text(
            text = "ᴛʜɪꜱ ʀᴇᴍɪɴᴅᴇʀ ɪꜱ ᴀʟʀᴇᴀᴅʏ ᴄᴏᴍᴘʟᴇᴛᴇᴅ ᴏʀ ᴇɪᴛʜᴇʀ ɴᴏᴛ ꜱᴇᴛ ʙᴀʙʏ🥀",
            reply_to_message_id = msg.message_id
        )
        return
    jobs[0].schedule_removal()
    msg.reply_text(
        text = "ᴅᴏɴᴇ ᴄʟᴇᴀʀᴇᴅ ᴛʜᴇ ʀᴇᴍɪɴᴅᴇʀ ʙᴀʙʏ🥀!",
        reply_to_message_id = msg.message_id
    )

def clear_all_reminders(update: Update, context: CallbackContext):
    user = update.effective_user
    msg = update.effective_message
    if user.id != OWNER_ID:
        msg.reply_text(
            text = "ᴡʜᴏ ᴛʜɪꜱ ɢᴜʏ ɴᴏᴛ ʙᴇɪɴɢ ᴛʜᴇ ᴏᴡɴᴇʀ ᴡᴀɴᴛꜱ ᴍᴇ ᴄʟᴇᴀʀ ᴀʟʟ ᴛʜᴇ ʀᴇᴍɪɴᴅᴇʀꜱ ʙᴀʙʏ🥀!?",
            reply_to_message_id = msg.message_id
        )
        return
    jobs = list(job_queue.jobs())
    unremoved_reminders = []
    for job in jobs:
        try:
            job.schedule_removal()
        except Exception:
            unremoved_reminders.append(job.name[1:])
    reply_text = "ᴅᴏɴᴇ ᴄʟᴇᴀʀᴇᴅ ᴀʟʟ ᴛʜᴇ ʀᴇᴍɪɴᴅᴇʀꜱ ʙᴀʙʏ🥀!\n\n"
    if len(unremoved_reminders) > 0:
        reply_text += "ᴇxᴄᴇᴘᴛ (<i>ᴛɪᴍᴇ ꜱᴛᴀᴍᴘꜱ ʜᴀᴠᴇ ʙᴇᴇɴ ᴍᴇɴᴛɪᴏɴᴇᴅ</i>):"
        for i, u in enumerate(unremoved_reminders):
            reply_text += f"\n{i+1}. <code>{u}</code>"
    msg.reply_text(
        text = reply_text,
        reply_to_message_id = msg.message_id,
        parse_mode = ParseMode.HTML
    )

def clear_all_my_reminders(update: Update, context: CallbackContext):
    user = update.effective_user
    msg = update.effective_message
    jobs = list(job_queue.jobs())
    if len(jobs) == 0:
        msg.reply_text(
            text = "ʏᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴀɴʏ ʀᴇᴍɪɴᴅᴇʀꜱ ʙᴀʙʏ🥀!",
            reply_to_message_id = msg.message_id
        )
        return
    unremoved_reminders = []
    for job in jobs:
        if job.name.endswith(str(user.id)):
            try:
                job.schedule_removal()
            except Exception:
                unremoved_reminders.append(job.name[1:])
    reply_text = "ᴅᴏɴᴇ ᴄʟᴇᴀʀᴇᴅ ᴀʟʟ ʏᴏᴜʀ ʀᴇᴍɪɴᴅᴇʀꜱ ʙᴀʙʏ🥀!\n\n"
    if len(unremoved_reminders) > 0:
        reply_text += "ᴇxᴄᴇᴘᴛ (<i>ᴛɪᴍᴇ ꜱᴛᴀᴍᴘꜱ ʜᴀᴠᴇ ʙᴇᴇɴ ᴍᴇɴᴛɪᴏɴᴇᴅ</i>):"
        for i, u in enumerate(unremoved_reminders):
            reply_text += f"\n{i+1}. <code>{u}</code>"
    msg.reply_text(
        text = reply_text,
        reply_to_message_id = msg.message_id,
        parse_mode = ParseMode.HTML
    )

__mod_name__ = "REMINDERS"
__help__ = """
  ➢ `/reminders`*:* ɢᴇᴛ ᴀ ʟɪꜱᴛ ᴏꜰ *ᴛɪᴍᴇꜱᴛᴀᴍᴘꜱ* ᴏꜰ ʏᴏᴜʀ ʀᴇᴍɪɴᴅᴇʀꜱ. 
  ➢ `/setreminder <time> <remind message>`*:* ꜱᴇᴛ ᴀ ʀᴇᴍɪɴᴅᴇʀ ᴀꜰᴛᴇʀ ᴛʜᴇ ᴍᴇɴᴛɪᴏɴᴇᴅ ᴛɪᴍᴇ.
  ➢ `/clearreminder <timestamp>`*:* ᴄʟᴇᴀʀꜱ ᴛʜᴇ ʀᴇᴍɪɴᴅᴇʀ ᴡɪᴛʜ ᴛʜᴀᴛ ᴛɪᴍᴇꜱᴛᴀᴍᴘ ɪꜰ ᴛʜᴇ ᴛɪᴍᴇ ᴛᴏ ʀᴇᴍɪɴᴅ ɪꜱ ɴᴏᴛ ʏᴇᴛ ᴄᴏᴍᴘʟᴇᴛᴇᴅ.
  ➢ `/clearmyreminders`*:* clears all the reminders of the user.
*Usage:*
  ➢ `/setreminder 30s reminder`*:* Here the time format is same as the time format in muting but with extra seconds(s)
  ➢ `/clearreminder 1234567890123456789`
"""

RemindersHandler = CommandHandler(['reminders', 'myreminders'], reminders, filters = Filters.chat_type.private, run_async=True)
SetReminderHandler = DisableAbleCommandHandler('setreminder', set_reminder, run_async=True)
ClearReminderHandler = DisableAbleCommandHandler('clearreminder', clear_reminder, run_async=True)
ClearAllRemindersHandler = CommandHandler(
    'clearallreminders', clear_all_reminders, filters = Filters.chat(OWNER_ID), run_async=True)
ClearALLMyRemindersHandler = CommandHandler(
    ['clearmyreminders', 'clearallmyreminders'], clear_all_my_reminders, filters = Filters.chat_type.private, run_async=True)

dispatcher.add_handler(RemindersHandler)
dispatcher.add_handler(SetReminderHandler)
dispatcher.add_handler(ClearReminderHandler)
dispatcher.add_handler(ClearAllRemindersHandler)
dispatcher.add_handler(ClearALLMyRemindersHandler)
