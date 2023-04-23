import json

from tgbot.api import send_message, forward_message, delete_message
from tgbot.storage import storage, Profile
from tgbot.config import FEEDBACK_CHAT_ID


def handle_feedback(msg):
    mid = msg['message_id']
    cid = msg['chat']['id']
    r = forward_message(cid, mid, FEEDBACK_CHAT_ID)
    support_msg_id = r['result']['message_id']
    # сохранение айди сообщения в приватной переписке с ботом
    storage.set(f'fbk-{support_msg_id}', json.dumps({
        "author_id": msg["from"]["id"],
        "message_id": mid,
        "chat_id": cid
    }))


def handle_answer(msg):
    print(f'handle answer from support')
    support_msg_id = str(msg['reply_to_message']['message_id'])
    # получение сохраненного айди сообщения из личной переписки с ботом
    stored_feedback = storage.get(f'fbk-{support_msg_id}')
    stored_feedback = json.loads(stored_feedback)
    r = send_message(f'{stored_feedback["chat_id"]}', msg['text'], reply_to=stored_feedback["message_id"])
    print(r)

