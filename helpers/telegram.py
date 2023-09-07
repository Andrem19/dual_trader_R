from decouple import config
from telegram import Bot

async def send_inform_message(message, image_path: str, send_pic: bool):
    try:
        api_token = config("API_TOKEN")
        chat_id = config("CHAT_ID")

        bot = Bot(token=api_token)

        response = None
        if send_pic:
            with open(image_path, 'rb') as photo:
                response = await bot.send_photo(chat_id=chat_id, photo=photo, caption=message)
        else:
            response = await bot.send_message(chat_id=chat_id, text=message)

        if response:
            pass
        else:
            print("Failed to send inform message.")
    except Exception as e:
        print("An error occurred:", str(e))