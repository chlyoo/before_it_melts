import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import config
import pytz
import melt_check
import redis
import datetime
# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

r = redis.from_url(config.REDIS_URL)
global db_keys
db_keys = r.keys(pattern='*')


# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.
def start(update, context):
    """Send a message when the command /help is issued."""
    user_id = update.message.from_user.id
    user_name = update.message.from_user.name
    logger.info((user_id,user_name))
    context.bot.send_message(chat_id=update.message.chat_id, text="안녕하세요. 녹기전에 봇입니다. /help 를 눌러서 사용법을 확인하세요")

def help(update, context):
    """Send a message when the command /help is issued."""
    context.bot.send_message(chat_id=update.message.chat_id, text="/register 라고 입력하시면 매일 오후 1시에 메뉴 알림을 받으실 수 "
                                                                  "있습니다.\n/menu 라고 입력하시면, 현재 메뉴를 불러올 수 있습니다.")

def register(update, context):
    """register chatroom for a regular notice"""
    global db_keys
    user_id = update.message.from_user.id
    user_name = update.message.from_user.name
    if update.message.chat.type=='group':
        group_id = update.message.chat_id
        group_name = update.message.chat.title + str(group_id)
        r.set(group_name, group_id)
        logger.info(('register',group_name, group_id))
        update.message.reply_text(f'{update.message.chat.title} group Chatroom has registered!')
    if update.message.chat.type == 'private':
        r.set(user_name, user_id)
        logger.info(('register',user_name,user_id))
        update.message.reply_text(f'{user_name} registered')
    db_keys = r.keys(pattern='*')

def deregister(update, context):
    global db_keys
    """deregister chatroom for a regular notice"""
    user_id = update.message.from_user.id
    user_name = update.message.from_user.name
    if update.message.chat.type=='group':
        group_id = update.message.chat_id
        group_name = update.message.chat.title + str(group_id)
        r.delete(group_name)
        logger.info(('deregister',group_name, group_id))
        update.message.reply_text(f'{update.message.chat.title} group Chatroom has unregistered!')
    if update.message.chat.type == 'private':
        r.delete(user_name)
        logger.info(('deregister',user_id,user_name))
        update.message.reply_text(f'{user_name} registered')
    db_keys = r.keys(pattern='*')

def menu(update, context):
    try:
        menu = melt_check.get_menus()
        menu_str = "\n".join(menu)
        update.message.reply_text(menu_str)
    except Exception as e:
        logger.warning(str(e))
        update.message.reply_text("에러가 발생했습니다.")

# def echo(update, context):
#     """Echo the user message."""
#     print(update.message.chat)
#     update.message.reply_text(update.message)

def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)

def morning(context: CallbackContext):
    global db_keys
    message = "좋은 아침입니다. 좋은 하루 보내세요"
    for keys in db_keys:
        id = r.get(keys).decode("UTF-8")
        context.bot.send_message(chat_id = id, text= message)

def notice(context: CallbackContext):
    global db_keys
    menu = melt_check.get_menus()
    menu_str = "\n".join(menu)
    message ="[메뉴공지]" + menu_str
    db_keys = r.keys(pattern='*')
    for keys in db_keys:
        try:
            id = r.get(keys).decode("UTF-8")
            context.bot.send_message(chat_id=id, text=message)
        except Exception as e:
            logger.warning(str(e))
            r.delete(keys)
            continue

def main():
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater(config.TELEGRAM_TOKEN, use_context=True)
    print(datetime.datetime.now())
    # Get the dispatcher to register handlers
    dp = updater.dispatcher
    jq = updater.job_queue

    # daily scheduled tasks
    # jq.run_once(morning,5)
    jq.run_daily(morning, days=(0, 1, 2, 3, 4, 5, 6), time=datetime.time(hour=8, minute=00, second=00, tzinfo=pytz.timezone('Asia/Seoul')))
    jq.run_daily(notice, days=(0, 1, 2, 3, 4, 5, 6), time=datetime.time(hour=13, minute=00, second=00, tzinfo=pytz.timezone('Asia/Seoul')))
                #-694717967

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("menu", menu))
    dp.add_handler(CommandHandler("register", register))
    dp.add_handler(CommandHandler("deregister", deregister))

    # on noncommand i.e message - echo the message on Telegram
    # dp.add_handler(MessageHandler(Filters.text, echo))

    # log all errors
    dp.add_error_handler(error)
    jq.start()
    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
