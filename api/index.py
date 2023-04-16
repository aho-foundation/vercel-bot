import os

from tgbot.rest import delete_message, register_webhook, send_message, ban_member, unban_member
from sanic import Sanic
from sanic.response import json, text


app = Sanic()
WEBHOOK = os.environ.get('VERCEL_URL')
CHAT_ID = os.environ.get('CHAT_ID').replace("-", "-100")
WELCOME_MSG = 'Добро пожаловть домой! Эта открытая беседа о Радужных Собраниях на русском языке. Пожалуйста, чтите Традиции и берегите друг друга.'

newcomers = {}


@app.route('/', methods=["GET", "PUT", "OPTIONS"])
async def register(req):
    r = register_webhook(WEBHOOK)
    print('\n\t\t\tWEBHOOK REGISTERED\n')
    return json(r.json())


@app.post('/')
async def handle(req):
    print(req)
    try:
        update = req.json
        print(update)
        msg = update.get('message')
        if msg['chat']['id'] == CHAT_ID:
            chat_id = msg['chat']['id']
            member_id = msg['user']['id']
            if msg['chat']['type'] == 'new_chat_member':
                newcomers[member_id] = 'newcomer'
                reply_markup = {
                    "inline_keyboard": [
                        [
                            {"text": "Всё понятно", "callback_data": "Всё понятно"},
                            {"text": "Доброе утро", "callback_data": "Доброе утро"}
                        ]
                    ]
                }
                welcome_msg_id = send_message(
                    chat_id,
                    WELCOME_MSG,
                    reply_to=msg['message_id'],
                    reply_markup=reply_markup
                )
                newcomers[member_id] = 'newcomer' + welcome_msg_id
            elif msg['chat']['type'] == 'text':
                data = newcomers[member_id]
                if data:
                    if data.startswith('newcomer'):
                        if 'text' in msg:
                            answer = msg['text']
                            if 'доброе утро' in answer.lower():
                                del newcomers[member_id]
                            else:
                                delete_message(msg['message_id'])
                        else:
                            callback_data = update['callback_query']['data']  
                            if callback_data == 'Всё понятно':
                                ban_member(member_id, chat_id)
                            elif callback_data == 'Доброе утро':
                                del newcomers[member_id]
                                delete_message(CHAT_ID, data.replace('newcomer', ''))
    except Exception:
        pass
    return text('ok')
