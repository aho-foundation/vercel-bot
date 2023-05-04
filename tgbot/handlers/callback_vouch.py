from tgbot.api import send_message, forward_message, delete_message, \
    approve_chat_join_request, edit_replymarkup, get_chat
from tgbot.storage import Profile, storage


def update_button(chat_id, member_id, text='❤️'):
    print('update reply markup')
    prevmsg_id = storage.get(f'btn-{chat_id}-{member_id}')
    if prevmsg_id:
        premsg_id = prevmsg_id.decode('utf-8')
    newcomer = Profile.get(member_id)
    amount = len(newcomer['parents']) + 1
    text += f' {amount}'
    rm = {
        "inline_keyboard": [
            [
                {
                    "text": text, 
                    "callback_data": 'vouch' + member_id
                }
            ]
        ]
    }
    r = edit_replymarkup(chat_id, prevmsg_id, reply_markup=rm)
    print(r)


def handle_button(callback_query):
    # получаем профиль нажавшего кнопку
    actor_id = str(callback_query['from']['id'])
    actor = Profile.get(actor_id, callback_query)

    callback_data = callback_query['data']
    if callback_data.startswith('vouch'):
        print(f'button pressed by {actor_id}')

        newcomer_id = callback_data[5:]
        print(f'button pressed for {newcomer_id}')

        newcomer = Profile.get(newcomer_id)
        print(f'newcomer profile {newcomer}')
        if newcomer_id == actor_id:
            # нажал сам, не реагируем, прописываем данные
            newcomer = Profile.get(newcomer_id, callback_query)
        else:
                # нажал кто-то другой

                if str(actor_id) not in newcomer['parents']:
                    print(f'save parent for {newcomer_id}')
                    newcomer['parents'].append(str(actor_id))
                    Profile.save(newcomer)

                if str(newcomer_id) not in actor['children']:
                    print(f'save child for {actor_id}')
                    actor['children'].append(str(newcomer_id))
                    Profile.save(actor)

                chat_id = str(callback_query['message']['chat']['id'])

                print('accept join request')
                r = approve_chat_join_request(chat_id, newcomer_id)
                print(r)

                update_button(chat_id, newcomer_id)