from models.db_manager import DBManager
from models.db_components import MongoDB, Redis
from melt_check import MeltCheck
from subscriptor import SubsCheck
import schedule
import time

import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import config
import pytz
import melt_check
import redis
import datetime

class TelegrmaBot():
    # Enable logging
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO)
    logger = logging.getLogger(__name__)
    tz = pytz.timezone('Asia/Seoul')
    service = {}
    def __init__(self, dbu, debug):
        self.dbu = dbu
        self.debug = debug


    # Define a few command handlers. These usually take the two arguments bot and
    # update. Error handlers also receive the raised TelegramError object in error.
    @staticmethod
    def start(update, context):
        """Send a message when the command /help is issued."""
        user_id = update.message.from_user.id
        user_name = update.message.from_user.name
        TelegrmaBot.logger.info((user_id,user_name))
        context.bot.send_message(chat_id=update.message.chat_id, text="안녕하세요. 녹기전에 봇입니다. /help 를 눌러서 사용법을 확인하세요")

    @staticmethod
    def help(update, context):
        """Send a message when the command /help is issued."""
        context.bot.send_message(chat_id=update.message.chat_id, text="/register 라고 입력하시면 매일 오후 1시에 메뉴 알림을 받으실 수 "
                                                                      "있습니다.\n/menu 라고 입력하시면, 현재 메뉴를 불러올 수 있습니다.")

    def register_chat(self, update, context):
        """register chatroom for a regular notice"""
        user_id = update.message.from_user.id
        user_name = update.message.from_user.name
        if update.message.chat.type=='group':
            group_id = update.message.chat_id
            group_name = update.message.chat.title + str(group_id)
            self.dbu.set_key(group_name, group_id)
            TelegrmaBot.logger.info(('register',group_name, group_id))
            update.message.reply_text(f'{update.message.chat.title} group Chatroom has registered!')
        if update.message.chat.type == 'private':
            self.dbu.set_key(user_name, user_id)
            TelegrmaBot.logger.info(('register',user_name,user_id))
            update.message.reply_text(f'{user_name} registered')

    def deregister_chat(self, update, context):
        """deregister chatroom for a regular notice"""
        user_id = update.message.from_user.id
        user_name = update.message.from_user.name
        if update.message.chat.type=='group':
            group_id = update.message.chat_id
            group_name = update.message.chat.title + str(group_id)
            self.dbu.delete_key(group_name)
            TelegrmaBot.logger.info(('deregister',group_name, group_id))
            update.message.reply_text(f'{update.message.chat.title} group Chatroom has unregistered!')
        if update.message.chat.type == 'private':
            self.dbu.delete_key(user_name)
            TelegrmaBot.logger.info(('deregister',user_id,user_name))
            update.message.reply_text(f'{user_name} registered')

    @staticmethod
    def menu(update, context):
        # tzinfo=pytz.timezone('Asia/Seoul')
        if datetime.datetime.now(tz=TelegrmaBot.tz).weekday() == 1:
            update.message.reply_text("매주 화요일은 휴일입니다.")
        try:
            menu = melt_check.get_menus()
            menu_str = "\n".join(menu)
            update.message.reply_text(menu_str)
        except Exception as e:
            TelegrmaBot.logger.warning(str(e))
            update.message.reply_text("에러가 발생했습니다.")

    @staticmethod
    def error(update, context):
        """Log Errors caused by Updates."""
        TelegrmaBot.logger.warning('Update "%s" caused error "%s"', update, context.error)

    def morning(self, context: CallbackContext):
        message = "좋은 아침입니다. 좋은 하루 보내세요"
        for keys in self.dbu.get_all_keys():
            id = self.dbu.get_key(keys).decode("UTF-8")
            context.bot.send_message(chat_id = id, text= message)

    def notice(self, context: CallbackContext):
        if datetime.datetime.now(tz=TelegrmaBot.tz).weekday() == 1:
            message = "매주 화요일은 휴일입니다."
            for keys in self.dbu.get_all_keys():
                try:
                    id = self.dbu.get_key(keys).decode("UTF-8")
                    context.bot.send_message(chat_id=id, text=message)
                except:
                    TelegrmaBot.logger.warning(str(e))
                    self.dbu.delete_key(keys)
                    continue
        menu = None # melt_check.get_menus()
        menu_str = "\n".join(menu)
        message ="[메뉴공지]" + menu_str
        for keys in self.dbu.get_all_keys():
            try:
                id = self.dbu.get_key(keys).decode("UTF-8")
                context.bot.send_message(chat_id=id, text=message)
            except Exception as e:
                TelegrmaBot.logger.warning(str(e))
                self.dbu.delete_key(keys)
                continue
    @staticmethod
    def cronjob():
        TelegrmaBot.service['meltcheck_mongo'].get_menu_data()

    def run(self):
        """Start the bot."""
        # Create the Updater and pass it your bot's token.
        # Make sure to set use_context=True to use the new context based callbacks
        # Post version 12 this will no longer be necessary
        updater = Updater(config.TELEGRAM_TOKEN, use_context=True)
        print(datetime.datetime.now(tz=TelegrmaBot.tz))
        # Get the dispatcher to register handlers
        dp = updater.dispatcher
        jq = updater.job_queue

        # daily scheduled tasks
        # jq.run_once(morning,5)
        jq.run_repeating(TelegrmaBot.cronjob, datetime.timedelta(minutes=30), job_kwargs=None)
        jq.run_daily(self.morning, days=(0, 1, 2, 3, 4, 5, 6), time=datetime.time(hour=8, minute=00, second=00, tzinfo=pytz.timezone('Asia/Seoul')))
        jq.run_daily(self.notice, days=(0, 1, 2, 3, 4, 5, 6), time=datetime.time(hour=13, minute=00, second=00, tzinfo=pytz.timezone('Asia/Seoul')))
                    #-694717967

        # on different commands - answer in Telegram
        dp.add_handler(CommandHandler("start", self.start))
        dp.add_handler(CommandHandler("help", self.help))
        dp.add_handler(CommandHandler("menu", self.menu))
        dp.add_handler(CommandHandler("register", self.register_chat))
        dp.add_handler(CommandHandler("deregister", self.deregister_chat))

        # on noncommand i.e message - echo the message on Telegram
        # dp.add_handler(MessageHandler(Filters.text, echo))

        # log all errors
        dp.add_error_handler(self.error)
        # Start the Bot
        updater.start_polling()

        # Run the bot until you press Ctrl-C or the process receives SIGINT,
        # SIGTERM or SIGABRT. This should be used most of the time, since
        # start_polling() is non-blocking and will stop the bot gracefully.
        updater.idle()

    @staticmethod
    def register(svc_name, svc_instance):
        TelegrmaBot.service[svc_name] = svc_instance


if __name__ == '__main__':
    # Database Setup
    meltcheck_mongo = MongoDB(config.MONGODB_URL, 'meltcheck', 27017, config.MONGODB_ID, config.MONGODB_PW)
    meltcheck_mongo.set_collection('menu')
    subscript_mongo = MongoDB(config.MONGODB_URL, 'subscriptor', 27017, config.MONGODB_ID, config.MONGODB_PW)
    subscript_mongo.set_collection('subslist')
    subscript_redis = Redis(config.REDIS_URL, 6379)

    # Service setup
    meltcheck_svc = MeltCheck(meltcheck_mongo, config.DEBUG)
    subsmongo_svc = SubsCheck(subscript_mongo, config.DEBUG)
    # subsredis_svc = SubsCheck(subscript_redis, config.DEBUG)


    bot = TelegrmaBot(subscript_redis, config.DEBUG)
    bot.register('meltcheck_mongo', meltcheck_svc)
    bot.register('subs_mongo', subsmongo_svc)
    bot.register('subs_redis', subscript_redis)
    bot.cronjob()
    bot.run()
