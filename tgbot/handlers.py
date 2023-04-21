from tgbot.api import send_message, forward_message, delete_message, \
    ban_member, set_chatpermissions
from tgbot.config import FEEDBACK_CHAT_ID, WELCOME_MSG, BUTTON_NO, \
    BUTTON_OK, CHAT_ID, BUTTON_OK2, REDIS_URL
import json
import redis

# сохраняет сессии и пересылаемые сообщения между перезагрузками
storage = redis.from_url(REDIS_URL)


def user_accept(chat_id, author):
    r = delete_message(CHAT_ID, author["welcome_id"])
    print(r.json())
    author["newcomer"] = False

    r = set_chatpermissions(CHAT_ID, { "can_send_messages": True })
    print(r.json())

    # set author as not a newcomer
    storage.set(f'usr-{author["id"]}', json.dumps(author))


def handle_feedback(msg):
    mid = msg['message_id']
    cid = msg['chat']['id']
    r = forward_message(cid, mid, FEEDBACK_CHAT_ID).json()
    support_msg_id = r['result']['message_id']
    # store private chat message id 
    # fbk-<support-chat-message-id> -> <private-chat-id>:<private-message-id>
    storage.set(f'fbk-{support_msg_id}', json.dumps({
        "author_id": msg["from"]["id"],
        "message_id": mid,
        "chat_id": cid
    }))


def handle_answer(msg):
    print(f'handle answer from support')
    support_msg_id = str(msg['reply_to_message']['message_id'])
    # get stored private chat id
    stored_feedback = storage.get(f'fbk-{support_msg_id}')
    stored_feedback = json.loads(stored_feedback)
    r = send_message(f'{stored_feedback["chat_id"]}', msg['text'], reply_to=stored_feedback["message_id"])  # notice 'u' before private chat ID
    print(r.json())


def handle_welcome(msg):
    chat_id = str(msg['chat']['id'])
    from_id = str(msg['from']['id'])
    member_id = str(msg['new_chat_member']['id'])
    s = {}
    if from_id == member_id:
        s["id"] = member_id
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
        print(r.json())
        print(f'welcome message id: {welcome_msg_id}')
        s["newcomer"] = True
        s["welcome_id"] = welcome_msg_id
        perms = {
            "can_send_messages": False
        }
        r = set_chatpermissions(CHAT_ID, perms)
        print(r.json())
    else:
        s['newcomer'] = False

    # create new member session
    storage.set(f'usr-{member_id}', json.dumps(s))


def handle_left(msg):
    print(f'handling member leaving')

    member_id = msg["left_chat_member"]["id"]

    # read member session
    s = storage.get(f'usr-{member_id}')
    if s:
        s = json.loads(s)
        r = delete_message(CHAT_ID, s['welcome_id'])
        print(r.json())

        # remove left member session
        storage.delete(f'usr-{member_id}')


def handle_text(msg):
    member_id = str(msg['from']['id'])

    # check if author is self-joined newcomer
    author = storage.get(f'usr-{member_id}')

    if author:
        author = json.loads(author)
        if author.get("newcomer"):
            print(f'new member speaks {msg["text"]}')
            answer = msg['text']
            if BUTTON_OK.lower() in answer.lower() or \
                BUTTON_OK2.lower() in answer.lower():
                print('found answer, cleanup')

                user_accept(CHAT_ID, author)

            #else:
            #    print('remove some message')
            #    r = delete_message(CHAT_ID, msg['message_id'])
            #    print(r.json())
        else:
            print(f'old member speaks {msg["text"]}')


def handle_button(callback_query):
    if 'reply_to_message' not in callback_query['message']:
        # удаляет сообщение с кнопкой, если оно ни на что не отвечает
        r = delete_message(CHAT_ID, callback_query['message'])
        print(r.json())
    else:
        member_id = str(callback_query['from']['id'])
        callback_data = callback_query['data']
        reply_owner = str(callback_query['message']['reply_to_message']['from']['id'])
        welcome_msg_id = str(callback_query['message']['message_id'])
        enter_msg_id = str(callback_query['message']['reply_to_message']['message_id'])
        if reply_owner == member_id:
            print(f'callback_query in {CHAT_ID}')
            
            # read session
            s = storage.get(f'usr-{member_id}')
            if s:
                s = json.loads(s)
            else:
                print('no user session found, create')
                s = {
                    'id': member_id,
                    'newcomer': True,
                    'welcome_id': welcome_msg_id
                }
                storage.set(f'usr-{member_id}', json.dumps(s))
            
            if callback_data == BUTTON_NO:
                print('wrong answer, cleanup')
                r = delete_message(CHAT_ID, enter_msg_id)
                print(r.json())
                r = delete_message(CHAT_ID, welcome_msg_id)
                print(r.json())

                # remove banned member session
                storage.delete(f'usr-{member_id}')

                print('ban member')
                r = ban_member(CHAT_ID, member_id)
                print(r.json())
            elif callback_data == BUTTON_OK:
                print('proper answer, cleanup')
                r = delete_message(CHAT_ID, welcome_msg_id)
                print(r.json())
                s['newcomer'] = False
                user_accept(CHAT_ID, s)