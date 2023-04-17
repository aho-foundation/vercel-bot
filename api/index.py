import os

from tgbot.rest import delete_message, register_webhook, send_message, ban_member, forward_message
from sanic import Sanic
from sanic.response import json, text
import redis
import json as codec

app = Sanic()

REDIS_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379'
storage = redis.from_url(REDIS_URL)  # сохраняет сессии и пересылаемые сообщения между перезагрузками

WEBHOOK = os.environ.get('VERCEL_URL')
CHAT_ID = os.environ.get('CHAT_ID').replace("-", "-100")
WELCOME_MSG = os.environ.get('WELCOME_MSG') or 'Welcome! Press the button'

BUTTON_OK = os.environ.get('BUTTON_OK') or 'Ok'
BUTTON_OK2 = os.environ.get('BUTTON_OK2') or 'I see'
BUTTON_NO = os.environ.get('BUTTON_NO') or 'No'

FEEDBACK_CHAT_ID = os.environ.get('FEEDBACK_CHAT_ID').replace("-", "-100")

app.config.REGISTERED = False


@app.route('/', methods=["GET"])
async def register(req):
    if not app.config.REGISTERED:
        r = register_webhook(WEBHOOK)
        print(f'\n\t\t\tWEBHOOK REGISTERED:\n{r.json()}')
        app.config.REGISTERED = True
        return json(r.json())
    return text('skipped')


@app.post('/')
async def handle(req):
    print(req)
    try:
        update = req.json
        if 'message' in update:
            print(update)
            msg = update.get('message', update.get('edited_message'))
            if msg['chat']['type'] == 'private':
                mid = msg['message_id']
                cid = msg['chat']['id']
                r = forward_message(cid, mid, FEEDBACK_CHAT_ID)
                print(r.json())
                storage.set(f'fbk-{cid}-{mid}', r['id'])
            elif str(msg['chat']['id']) == CHAT_ID:
                print(f'message in chat')
                if 'new_chat_member' in msg:
                    chat_id = str(msg['chat']['id'])
                    from_id = str(msg['from']['id'])
                    member_id = str(msg['new_chat_member']['id'])
                    s = { 
                        "enter_id": msg['message_id']
                    }
                    if from_id == member_id:
                        print(f'new self-joined member {member_id}')
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
                        s["newcomer"] = True
                        s["welcome_id"] = welcome_msg_id
                    else:
                        s['newcomer'] = False

                    # create session
                    storage.set(f'usr-{member_id}', codec.dumps(s))

                elif 'text' in msg:
                    chat_id = str(msg['chat']['id'])
                    member_id = str(msg['from']['id'])

                    # check is author is selfjoined newcomer
                    author = storage.get(f'usr-{member_id}')

                    if author:
                        author = codec.parse(author)
                        if author.get("newcomer"):
                            print(f'new member speaks {msg["text"]}')
                            answer = msg['text']
                            if BUTTON_OK.lower() in answer.lower() or \
                                BUTTON_OK2.lower() in answer.lower():
                                print('found answer, cleanup')
                                r = delete_message(CHAT_ID, author["welcome_id"])
                                print(r.json())
                                author["newcomer"] = False

                                # set author as not a newcomer
                                storage.set(f'usr-{member_id}', codec.dumps(author))

                            else:
                                print('remove some message')
                                r = delete_message(CHAT_ID, msg['message_id'])
                                print(r.json())
                        else:
                            print(f'old member speaks {msg["text"]}')
        if 'callback_query' in update:
            callback_query = update['callback_query']
            chat_id = str(callback_query['message']['chat']['id'])
            if chat_id == CHAT_ID:
                member_id = str(callback_query['from']['id'])
                callback_data = callback_query['data']
                reply_owner = str(callback_query['message']['reply_to_message']['from']['id'])
                if reply_owner == member_id:
                    print(update)
                    print(f'callback_query in {CHAT_ID}')
                    s = storage.get(f'usr-{member_id}')
                    if s:
                        s = codec.parse(s)
                    if callback_data == BUTTON_NO:
                        print('wrong answer, cleanup')
                        r = delete_message(CHAT_ID, s['enter_id'])
                        print(r.json())
                        r = delete_message(CHAT_ID, s['welcome_id'])
                        print(r.json())
                        storage.delete(f'usr-{member_id}')
                        print('ban member')
                        r = ban_member(CHAT_ID, member_id)
                        print(r.json())
                    elif callback_data == BUTTON_OK:
                        print('proper answer, cleanup')
                        r = delete_message(CHAT_ID, s['welcome_id'])
                        print(r.json())
                        s['newcomer'] = False
                        storage.set(f'usr-{member_id}', codec.dumps(s))
    except Exception:
        pass
    return text('ok')
