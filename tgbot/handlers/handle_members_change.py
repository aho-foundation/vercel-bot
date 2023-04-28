from tgbot.handlers.send_button import show_request_msg
from tgbot.api import unmute_member, mute_member, delete_message
from tgbot.storage import Profile, storage

def handle_join(msg):
    chat_id = str(msg['chat']['id'])
    from_id = str(msg['from']['id'])

    actor = Profile.get(from_id, msg)

    newcomer_id = str(msg['new_chat_member']['id'])
    if from_id == newcomer_id:
        if len(actor['parents']) == 0:
            # показываем сообщение с кнопкой "поручиться"
            show_request_msg(msg)

            # до одобрения - мьют
            r = mute_member(chat_id, newcomer_id)
            print(r)

        else:
            # за пользователя поручились ранее
            pass
    else:
        # пользователи приглашены другим участником
        print(f'{len(msg["new_chat_members"])} members were invited by {from_id}')    
        for m in msg['new_chat_members']:
            newcomer = Profile.get(m['id'])
            newcomer['parents'].append(from_id)
            Profile.save(newcomer)
            actor['children'].append(m['id'])
            r = unmute_member(chat_id, newcomer['id'])
            print(r)

        # обновляем профиль пригласившего
        Profile.save(actor)


def handle_left(msg):
    print(f'handling member leaving')
    member_id = msg["left_chat_member"]["id"]
    chat_id = msg['chat']['id']

    # удаление сообщения с кнопкой в этом чате
    prev_msg = storage.get(f'btn-{chat_id}-{member_id}')
    if prev_msg_id:
        r = delete_message(chat_id, prev_msg['id'])
        print(r)
        storage.remove(f'btn-{chat_id}-{member_id}')


