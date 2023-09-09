from telegram import Update, Bot
import helpers.telegr as tel
from decouple import config
from telegram.ext import ContextTypes
import helpers.services as serv
import helpers.saldo as sal
import helpers.visualizer as vis
from models.settings import Settings
from models.position import Position
import shared_vars as sv

telegram_bot_api_key = config('API_TOKEN_1')

async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        coin = sv.settings_gl.coin
        exchange = sv.settings_gl.exchange
        bot = Bot(token=telegram_bot_api_key)
        chat_id = update.message.chat_id
        await bot.send_message(chat_id=chat_id, text=f'{coin}-{exchange} - Alive!')

async def request(request: str, settings: Settings):
    commands = request.split(' ')
    if commands[0] == f'{settings.coin}-{settings.exchange}' or commands[0] == '-':
        if commands[1] == 'tr' or commands[1] == 'Tr':
            await trend(commands[2], settings)
        if commands[1] == 'ph' or commands[1] == 'Ph':
            await pos_history(commands[2], settings)
          

async def trend(date_str: str, settings: Settings):
    saldos = sal.load_saldo()
    filtered_saldos = serv.filter_list_by_timestamp(saldos, serv.convert_to_timestamp(date_str))
    path = vis.plot_time_series(filtered_saldos, True, settings.border_saldo)
    await tel.send_inform_message(f'{settings.coin}-{settings.exchange}', path, True)

async def pos_history(number: str, settings: Settings):
    num = int(number)
    possitions = serv.read_deser_positions(settings.coin)
    if num > 2:
        await tel.send_inform_message('You cant load more then 2 possition', '', False)
    else:
        res_pos = possitions[-num:]
        await tel.send_inform_message(Position.parse_to_pretty_string(res_pos), '', False)
    

     