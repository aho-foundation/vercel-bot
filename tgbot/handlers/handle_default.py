from tgbot.api import send_message, delete_message, get_chat_administrators
from tgbot.storage import Profile
from tgbot.handlers.send_button import show_request_msg


def handle_default(msg):
    print(f'default handler for all messages')
    chat_id = str(msg['chat']['id'])
    from_id = str(msg['from']['id'])
    sender = Profile.get(from_id, msg)

    if msg['text'].startswith('/my'):
        # команда в групповом чате
        print(f'remove some messages in group chat')

        # удалить сообщение с командой /my
        r = delete_message(chat_id, msg['message_id'])
        print(r)

        # удалить предыдушее сообщение с кнопкой в этом чате
        if sender['request_msg_id'].startswith(chat_id):
            chat_id, rmid = sender['request_msg_id'].split(':')
            r = delete_message(chat_id, rmid)
            print(r)

        # показать новое сообщение с кнопкой
        request_msg_id = show_request_msg(msg)
        sender['request_msg_id'] = f'{chat_id}:{request_msg_id}'
    else:
        # любое другое сообщение
        if len(sender['parents']) == 0:
            # владелец чата автоматически ручается
            print(f'setting owner as parent for {from_id}')
            r = get_chat_administrators(chat_id)
            print(r)
            
            owner_id = r['result'][0]['id']  # DEBUG!!

            sender['parents'].append(owner_id)
            
            # обновляем профиль владельца
            owner = Profile.get(owner_id)
            owner['children'].append(from_id)
            Profile.save(owner)

    # сохранить профиль отправителя
    Profile.save(sender)