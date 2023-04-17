import os

from tgbot.rest import delete_message, register_webhook, send_message, ban_member, unban_member
from sanic import Sanic
from sanic.response import json, text


app = Sanic()

WEBHOOK = os.environ.get('VERCEL_URL')
CHAT_ID = os.environ.get('CHAT_ID').replace("-", "-100")
WELCOME_MSG = os.environ.get('WELCOME_MSG') or 'Welcome! Press the button'

BUTTON_OK = os.environ.get('BUTTON_OK') or 'Ok'
BUTTON_OK2 = os.environ.get('BUTTON_OK2') or 'I see'
BUTTON_NO = os.environ.get('BUTTON_NO') or 'No'

newcomers = {}
app.config.REGISTERED = False


@app.route('/', methods=["GET"])
async def register(req):
    if not app.config.REGISTERED:
        r = register_webhook(WEBHOOK)
        print(f'\n\t\t\tWEBHOOK REGISTERED:\n{r.json()}')
        app.config.REGISTERED = True
    return json(r.json())


@app.post('/')
async def handle(req):
    print(req)
    try:
        update = req.json
        print(update)
        msg = update.get('message', update.get('my_chat_member'))
        if msg:
            if str(msg['chat']['id']) == CHAT_ID:
                print(f'message in chat')
                if 'new_chat_member' in msg:
                    chat_id = str(msg['chat']['id'])
                    member_id = str(msg['new_chat_member']['id'])
                    print(f'new member {member_id}')
                    reply_markup = {
                        "inline_keyboard": [
                            [
                                {"text": BUTTON_NO, "callback_data": BUTTON_NO},
                                {"text": BUTTON_OK, "callback_data": BUTTON_OK}
                            ]
                        ]
                    }
                    r = send_message(
                        chat_id,
                        WELCOME_MSG,    
                        reply_to=msg['message_id'],
                        reply_markup=reply_markup
                    )
                    welcome_msg_id = r.json()['result']['message_id']
                    print(f'welcome message id: {welcome_msg_id}')
                    newcomers[member_id] = f'newcomer:{msg["message_id"]}:{welcome_msg_id}'
                elif 'text' in msg:
                    chat_id = str(msg['chat']['id'])
                    member_id = str(msg['from']['id'])
                    if member_id in newcomers:
                        print(f'new member speak {msg["text"]}')
                        if newcomers[member_id].startswith('newcomer'):
                            print('watched newcomer')
                            answer = msg['text']
                            if BUTTON_OK.lower() in answer.lower() or BUTTON_OK2.lower() in answer.lower():
                                print('found answer, cleanup')
                                [_, enter_msg, welcome_msg] = newcomers[member_id].split(':')
                                r = delete_message(CHAT_ID, welcome_msg)
                                print(r.json())
                                newcomers[member_id] = None
                            else:
                                print('remove some message')
                                r = delete_message(CHAT_ID, msg['message_id'])
                                print(r.json())
                    else:
                        print(f'old member speak {msg["text"]}')
        if 'callback_query' in update:
            callback_query = update['callback_query']
            chat_id = str(callback_query['message']['chat']['id'])
            if chat_id == CHAT_ID:
                print(f'callback_query in {CHAT_ID}')
                member_id = str(callback_query['from']['id'])
                callback_data = callback_query['data']
                reply_owner = str(callback_query['message']['reply_to_message']['from']['id'])
                if reply_owner == member_id:
                    if callback_data == BUTTON_NO:
                        print('wrong answer, cleanup')
                        [_, enter_msg, welcome_msg] = newcomers[member_id].split(':')
                        r = delete_message(CHAT_ID, enter_msg)
                        print(r.json())
                        r = delete_message(CHAT_ID, welcome_msg)
                        print(r.json())
                        newcomers[member_id] = None
                        print('ban member')
                        r = ban_member(CHAT_ID, member_id)
                        print(r.json())
                    elif callback_data == BUTTON_OK:
                        print('proper answer, cleanup')
                        [_, enter_msg, welcome_msg] = newcomers[member_id].split(':')
                        r = delete_message(CHAT_ID, welcome_msg)
                        print(r.json())
                        newcomers[member_id] = None
    except Exception:
        pass
    return text('ok')
