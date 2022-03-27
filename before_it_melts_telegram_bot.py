import logging
#import telegram
#import telegram.ext
import os
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import secrets
import melt_check
# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.
def start(update, context):
    """Send a message when the command /start is issued."""
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
    update.message.reply_text(update.message.text)


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def _send(update, context):
    global cur_dir
    fpath = str(update.message.text).split()
    # fpath[0] : /send
    # fpath[1] : target file
    flist = [str(x) for x in cur_dir.iterdir() if not x.is_dir()]

    for item in flist:
        if fpath[1] in item:
            f = open(item, "rb")
            context.bot.send_document(chat_id=update.message.chat_id, document=f)
            break

def main():
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater(secrets.TELEGRAM_TOKEN, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("send", _send))
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

