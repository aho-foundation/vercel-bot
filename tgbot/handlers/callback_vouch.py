from tgbot.api import send_message, forward_message, delete_message, \
    approve_chat_join_request, unmute_member, edit_replymarkup, get_chat
from tgbot.storage import Profile, storage


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

                if actor_id not in newcomer['parents']:
                    print(f'save parent for {newcomer_id}')
                    newcomer['parents'].append(actor_id)
                    Profile.save(newcomer)

                if newcomer_id not in actor['children']:
                    print(f'save child for {actor_id}')
                    actor['children'].append(newcomer_id)
                    Profile.save(actor)

                chat_id = str(callback_query['message']['chat']['id'])

                print('accept join request')
                r = approve_chat_join_request(chat_id, newcomer_id)
                print(r)

                print('update reply markup')
                prevmsg_id = storage.get(f'btn-{chat_id}-{newcomer_id}').decode('utf-8')
                amount = len(newcomer['parents']) + 1
                rm = {
                    "inline_keyboard": [
                        [
                            {
                                "text": '❤️' + f'({amount})', 
                                "callback_data": 'vouch' + newcomer_id
                            }
                        ]
                    ]
                }
                r = edit_replymarkup(chat_id, premsg_id, reply_markup=rm)
                print(r)

                if not r.get('ok'):         
                    print('getting chat permissions')     
                    r = get_chat(chat_id)
                    print(r)
                    perms = r['result']['permissions']
                    print('try to unmute newcomer')
                    r = unmute_member(chat_id, newcomer_id, chat_permissions=perms)
                    print(r)