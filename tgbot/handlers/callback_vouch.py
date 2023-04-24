from tgbot.api import send_message, forward_message, delete_message
from tgbot.storage import Profile
from tgbot.config import BUTTON_VOUCH


def handle_button(callback_query):
    # получаем профиль нажавшего кнопку
    actor_id = str(callback_query['from']['id'])
    actor = Profile.get(actor_id, callback_query)

    callback_data = callback_query['data']
    if callback_data.startswith(BUTTON_VOUCH):
        print(f'vouch button pressed by {actor_id}')

        newcomer_id = callback_data[len(BUTTON_VOUCH):]
        newcomer = Profile.get(newcomer_id)
        if newcomer_id == actor_id:
            # нажал сам, не реагируем, прописываем данные
            newcomer = Profile.get(newcomer_id, callback_query)
        elif newcomer_id not in actor['children'] and \
            actor_id not in newcomer['parents']:
                newcomer['parents'].append(actor_id)
                actor['children'].append(newcomer_id)
                Profile.save(newcomer)
                Profile.save(actor)
                try:
                    chat_id = str(callback_query['message']['chat']['id'])

                    print('unmute newcomer')
                    r = unmute_member(chat_id, newcomer_id)
                    print(r)

                    print('accept join request')
                    r = approve_chat_join_request(chat_id, newcomer_id)
                    print(r)

                except:
                    pass
       