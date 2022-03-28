import logging
#import telegram
#import telegram.ext
import os
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import secrets
import melt_check
import redis
import datetime
# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

r = redis.from_url(secrets.REDIS_URL)
db_keys = r.keys(pattern='*')

# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.
def start(update, context):
    """Send a message when the command /start is issued."""
    user_id = update.message.from_user.id
    user_name = update.message.from_user.name
    r.set(user_name, user_id)
    print(user_id, user_name)
    update.message.reply_text('Hi!')


def help(update, context):
    """Send a message when the command /help is issued."""
    update.message.reply_text('Help!')

def menu(update, context):
    try:
        menu = melt_check.get_menus()
        menu_str = "\n".join(menu)
        update.message.reply_text(menu_str)
    except Exception as e:
        update.message.reply_text(str(e))

def echo(update, context):
    """Echo the user message."""
    print(update.message.chat_id)
    update.message.reply_text(update.message.chat_id)


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)

def morning(context: CallbackContext):
    message = "좋은 아침입니다. 좋은 하루 보내세요"

    for keys in db_keys:
        id = r.get(keys).decode("UTF-8")
        context.bot.send_message(chat_id = id, text= message)


def notice(context: CallbackContext):
    menu = melt_check.get_menus()
    menu_str = "\n".join(menu)
    message = menu_str
    for keys in  db_keys:
        id = r.get(keys).decode("UTF-8")
        context.bot.send_message(chat_id=id, text=message)


def main():
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater(secrets.TELEGRAM_TOKEN, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher
    jq = updater.job_queue

    # daily scheduled tasks
    # jq.run_once(morning,5)
    job_daily = jq.run_daily(morning, days=(0, 1, 2, 3, 4, 5, 6), time=datetime.time(hour=8, minute=00, second=00))
    job_daily2 = jq.run_daily(notice, days=(0, 1, 2, 3, 4, 5, 6), time=datetime.time(hour=13, minute=00, second=00))
                #-694717967

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("menu", menu))

    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(MessageHandler(Filters.text, echo))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()

