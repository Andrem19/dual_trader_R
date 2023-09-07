import json
from exchange_workers.bybit_http import BybitAPI
import signal_handler.bot_commands as bc
import datetime
from models.settings import Settings
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, CommandHandler, filters
from decouple import config
from telegram import Update, Bot
import signal_handler.work as work
import main as m

app = None
runner = None

def open_worker():
    global app, runner, settings
    settings = None
    with m.global_var_lock:
        settings = m.settings_gl
    telegram_bot_api_key = config('SIGNAL_BOT')
    async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        global settings
        signals = update.message.text
        try:
            sign_dic = json.loads(signals)
        except json.JSONDecodeError:
            await bc.request(signals, settings)
        else:
            timestamp = sign_dic['timestamp']
            if m.handler_lock:
                return

            m.handler_lock = True
            
            if timestamp+25 > datetime.datetime.now().timestamp() or timestamp == 111 :
                with m.global_var_lock:
                    print(f'{signals}')
                    signal = sign_dic['DOTUSDT']

                if signal != 3:
                    resp = BybitAPI.get_position_info(settings.coin)
                    if float(resp['size']) == 0:
                        settings = Settings(settings.coin, settings.t)
                        settings.from_json()
                        with m.global_var_lock:
                            m.settings_gl = settings
                        await work.open_position(settings, signal)
            else:
                pass

            m.handler_lock = False

    app = ApplicationBuilder().token(telegram_bot_api_key).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handler))
    app.add_handler(CommandHandler('ping', bc.ping))
    runner = app.run_polling()


