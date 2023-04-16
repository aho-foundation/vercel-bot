import os

from tgbot.rest import delete_message, register_webhook, send_message, ban_member, unban_member
from sanic import Sanic
from sanic.response import json, text


app = Sanic()

WEBHOOK = os.environ.get('VERCEL_URL')
CHAT_ID = os.environ.get('CHAT_ID').replace("-", "-100")
WELCOME_MSG = os.environ.get('WELCOME_MSG') or 'Welcome! Press the button'

BUTTON_OK = os.environ.get('BUTTON_OK') or 'Ok'
BUTTON_NO = os.environ.get('BUTTON_NO') or 'No'

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
        # print(update)
        msg = update.get('message', update.get('my_chat_member'))
        if str(msg['chat']['id']) == CHAT_ID:
            print(f'message in chat')
            if 'new_chat_member' in msg:
                chat_id = str(msg['chat']['id'])
                member_id = str(msg['new_chat_member']['id'])
                print(f'new member {member_id}')
                newcomers[member_id] = 'newcomer'
                reply_markup = {
                    "inline_keyboard": [
                        [
                            {"text": BUTTON_NO, "callback_data": BUTTON_NO},
                            {"text": BUTTON_OK, "callback_data": BUTTON_OK}
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
            elif 'text' in msg:
                chat_id = str(msg['chat']['id'])
                member_id = str(msg['from']['id'])
                if member_id in newcomers:
                    if newcomers[member_id].startswith('newcomer'):
                        answer = msg['text']
                        if BUTTON_OK.lower() in answer.lower():
                            del newcomers[member_id]
                        else:
                            delete_message(msg['message_id'])
        if 'callback_query' in update:
            print(f'callback_query')
            callback_query = update['callback_query']
            chat_id = str(callback_query['message']['chat']['id'])
            if chat_id == CHAT_ID:
                member_id = str(callback_query['from']['id'])
                callback_data = callback_query['data']  
                if callback_data == BUTTON_NO:
                    ban_member(member_id, CHAT_ID)
                elif callback_data == BUTTON_OK:
                    del newcomers[member_id]
                    delete_message(CHAT_ID, newcomers[member_id].replace('newcomer', ''))
    except Exception:
        pass
    return text('ok')
