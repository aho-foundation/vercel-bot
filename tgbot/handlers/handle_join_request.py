from tgbot.api import approve_chat_join_request, delete_message           
from tgbot.handlers.send_button import show_request_msg
from tgbot.storage import Profile


def handle_join_request(msg):
    print(f'handle join request {msg}')
    chat_id = str(msg['chat']['id'])
    from_id = str(msg['from']['id'])
    actor = Profile.get(from_id, msg)

    if len(actor['parents']) == 0:
        # показываем сообщение с кнопкой "поручиться"
        request_msg_id = show_request_msg(msg)
        # удаляем предыдущее сообщение с кнопкой в этом чате
        if actor['request_msg_id'].startswith(chat_id):
            chat_id, rmid = actor['request_msg_id'].split(':')
            r = delete_message(chat_id, rmid)
            print(r)
        actor['request_msg_id'] = f'{chat_id}:{request_msg_id}'
    else:
        # за пользователя поручились ранее
        r = approve_chat_join_request(chat_id, from_id)
        print(r)
    Profile.save(actor)

