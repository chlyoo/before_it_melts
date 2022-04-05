import datetime
import logging
import pytz
import telegram
import random
from telegram.ext import Updater, CommandHandler, CallbackContext, ContextTypes
from melt_check import MeltCheck
from models.db_components import MongoDB, Redis
import config
import functools

class TelegramBot():
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO)
    logger = logging.getLogger(__name__)
    tz = pytz.timezone('Asia/Seoul')
    service = {}

    def __init__(self, dbu, debug):
        self.dbu = dbu
        self.debug = debug
        self.menu_data = None
        self.service = TelegramBot.service


    def _decorator(self, func):
        def wrapper(*args, **kwargs):
            try:
                if args:
                    if len(args) == 2:
                        if type(args[0]) is telegram.update.Update:
                            self.logger.info(
                            f'UserCall ({func.__name__.upper()}) "CHAT: {args[0].message.chat_id} USER: {args[0].message.from_user.id} NAME: {args[0].message.from_user.name}"')
                        else:
                            self.logger.debug(f'SystemCall ({func.__name__.upper()})')
                    if len(args) == 1:
                        self.logger.info(f'BotCall ({func.__name__.upper()})')
                else:
                    self.logger.debug(f'SystemCall ({func.__name__.upper()})')
            except Exception as e:
                self.logger.warning(e)
            finally:
                result = func(*args, **kwargs)
            return result
        return wrapper

    def __getattribute__(self, item):
        value = object.__getattribute__(self, item)
        if callable(value):
            decorator = object.__getattribute__(self, '_decorator')
            return decorator(value)
        return value

    def start(self, update, context):
        """Send a message when the command /help is issued."""
        user_id = update.message.from_user.id
        user_name = update.message.from_user.name
        context.bot.send_message(chat_id=update.message.chat_id, text="안녕하세요. 녹기전에 봇입니다. /help 를 눌러서 사용법을 확인하세요")

    def help(self, update, context):
        """Send a message when the command /help is issued."""
        context.bot.send_message(chat_id=update.message.chat_id, text="/register 라고 입력하시면 매일 오후 1시에 메뉴 알림을 받으실 수 "
                                                                      "있습니다.\n/menu 라고 입력하시면, 현재 메뉴를 불러올 수 있습니다.")

    def register_chat(self, update, context):
        """register chatroom for a regular notice"""
        user_id = update.message.from_user.id
        user_name = update.message.from_user.name
        if update.message.chat.type == 'group':
            group_id = update.message.chat_id
            group_name = update.message.chat.title + str(group_id)
            self.dbu.set_key(group_name, group_id)
            update.message.reply_text(f'{update.message.chat.title} group Chatroom has registered!')
        if update.message.chat.type == 'private':
            self.dbu.set_key(user_name, user_id)
            update.message.reply_text(f'{user_name} registered')

    def deregister_chat(self, update, context):
        """deregister chatroom for a regular notice"""
        user_id = update.message.from_user.id
        user_name = update.message.from_user.name
        if update.message.chat.type == 'group':
            group_id = update.message.chat_id
            group_name = update.message.chat.title + str(group_id)
            self.dbu.delete_key(group_name)
            update.message.reply_text(f'{update.message.chat.title} group Chatroom has unregistered!')
        if update.message.chat.type == 'private':
            self.dbu.delete_key(user_name)
            update.message.reply_text(f'{user_name} registered')

    def menu(self, update, context):
        if datetime.datetime.now(tz=self.tz).weekday() == 1:
            update.message.reply_text(self.get_holiday_message())
            return
        try:
            update.message.reply_text(self.get_menu_message())
        except Exception as e:
            self.logger.warning(str(e))
            update.message.reply_text("에러가 발생했습니다.")

    def error(self, update, context):
        """Log Errors caused by Updates."""
        self.logger.warning('Update "%s" caused error "%s"', update, context.error)
        if hasattr(update, 'message'):
            context.bot.send_message(chat_id=update.message.chat_id, text="에러가 발생했습니다. by error function")

    def morning(self, context: CallbackContext):
        message = "좋은 아침입니다. 좋은 하루 보내세요"
        self.send_message_to_subscribers(context, message)

    def goodjob(self, context: CallbackContext):
        message_list = ["오늘 하루도 고생했어요~♥",
                        "수고했어요 :D 푹 쉬어요~",
                        "사랑해요♥",
                        "난 늘 응원해!",
                        "넌 잘하고 있어",
                        ]
        message = random.choice(message_list)
        self.send_message_to_subscribers(context, message)

    def get_menudata(self):
        menu = self.service['meltcheck_mongo'].request_data()
        if menu == None:
            self.service['meltcheck_mongo'].sync()
            return self.service['meltcheck_mongo'].request_data()
        return menu

    def get_menu_message(self, raw_menu=None):
        menu = self.get_menudata()
        menu_str = "\n".join(menu)
        return menu_str

    def get_notice_message(self, raw_menu=None):
        menu = self.get_menudata()
        if raw_menu:
            menu = raw_menu
        menu_str = "\n".join(menu)
        message = "[메뉴공지]\n" + menu_str +"\n 알림 해제를 원하시면 /deregister 를 입력해주세요"
        return message

    def get_holiday_message(self, custom_message=None):
        if custom_message:
            return custom_message
        message = "매주 화요일은 휴일입니다."
        return message

    def send_message_to_subscribers(self, context: CallbackContext, message):
        for keys in self.dbu.get_all_keys():
            key_id = keys.decode('UTF-8')
            if key_id.startswith("backup"):
                continue
            try:
                id = self.dbu.get_key(keys).decode("UTF-8")
                context.bot.send_message(chat_id=id, text=message)
            except Exception as e:
                self.dbu.delete_key(keys)
                self.logger.warning(str(e))
                continue

    def notice(self, context: CallbackContext, custom_message=None):
        message = self.get_notice_message()
        if datetime.datetime.now(tz=TelegramBot.tz).weekday() == 1:
            message = self.get_holiday_message()
        if custom_message:
            message = custom_message
        self.send_message_to_subscribers(context, message)

    # notice debug
    def call_notice(self, update, context):
        self.notice(context ,custom_message="공지 테스트")

    def cronjob(self, context: CallbackContext):
        self.service['meltcheck_mongo'].sync()
        self.menu_data = self.service['meltcheck_mongo'].request_data()

    @staticmethod
    def register(svc_name: str, svc_instance):
        TelegramBot.service[svc_name] = svc_instance

    def run(self):
        """Start the bot."""
        updater = Updater(config.TELEGRAM_TOKEN, use_context=True)
        # Get the dispatcher to register handlers
        dp = updater.dispatcher
        jq = updater.job_queue
        # daily scheduled tasks
        jq.run_repeating(self.cronjob, interval=1800, first=30)
        # datetime.timedelta(minutes=30), first=datetime.timedelta(minutes=0), context=updater.)
        jq.run_daily(self.morning, days=(0, 1, 2, 3, 4, 5, 6),
                     time=datetime.time(hour=8, minute=00, second=00, tzinfo=pytz.timezone('Asia/Seoul')))

        jq.run_daily(self.goodjob, days=(0, 1, 2, 3, 4),
                     time=datetime.time(hour=17, minute=00, second=00, tzinfo=pytz.timezone('Asia/Seoul')))

        #jq.run_daily(self.notice, days=(0, 1, 2, 3, 4, 5, 6),time=datetime.time(hour=16, minute=10, second=00, tzinfo=pytz.timezone('Asia/Seoul')))
        jq.run_daily(self.notice, days=(0, 1, 2, 3, 4, 5, 6),
                     time=datetime.time(hour=13, minute=00, second=00, tzinfo=pytz.timezone('Asia/Seoul')))
        # on different commands - answer in Telegram
        dp.add_handler(CommandHandler("start", self.start))
        dp.add_handler(CommandHandler("help", self.help))
        dp.add_handler(CommandHandler("menu", self.menu))
        dp.add_handler(CommandHandler("register", self.register_chat))
        dp.add_handler(CommandHandler("deregister", self.deregister_chat))

        # notice debug
        if config.DEBUG:
            dp.add_handler(CommandHandler("notice", self.call_notice))
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


if __name__ == '__main__':
    # Database Setup
    meltcheck_mongo = MongoDB(config.MONGODB_URL, 'meltcheck', 27017, config.MONGODB_ID, config.MONGODB_PW)
    meltcheck_mongo.set_collection('menu')
    subscript_redis = Redis(config.REDIS_URL, config.REDIS_PORT, config.REDIS_ID,  config.REDIS_PW)

    # Service setup
    meltcheck_svc = MeltCheck(meltcheck_mongo, config.DEBUG)
    meltcheck_svc.request_data()
    #bot setup
    bot = TelegramBot(subscript_redis, config.DEBUG)

    #register service on bot
    bot.register('meltcheck_mongo', meltcheck_svc)

    #run
    bot.run()
