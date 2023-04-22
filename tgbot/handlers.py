from tgbot.api import send_message, forward_message, delete_message, \
    ban_member, unban_member, mute_member, unmute_member, \
    approve_chat_join_request, send_graph
from tgbot.graph import generate_chart
from tgbot.config import REDIS_URL, FEEDBACK_CHAT_ID, BUTTON_VOUCH, NEWCOMER_MSG
import json
import redis
from tgbot.profile import Profile as ProfileObj


# сохраняет сессии и пересылаемые сообщения между перезагрузками
storage = redis.from_url(REDIS_URL)

# хранение необходимой информации о пользователях
Profile = ProfileObj(storage)

def newcomer_show(msg):
    reply_markup = {
        "inline_keyboard": [
            [
                {
                    "text": BUTTON_VOUCH, 
                    "callback_data": BUTTON_VOUCH + str(msg['from']['id'])
                }
            ]
        ]
    }
    identity = f"{msg['from']['first_name']} {msg['from'].get('last_name', '')}"
    if 'username' in msg['from']:
        identity += f" @{msg['from']['username']}"
    r = send_message(
        msg['chat']['id'],
        NEWCOMER_MSG + identity,   
        reply_to=msg['message_id'],
        reply_markup=reply_markup
    )
    welcome_msg_id = r.json()['result']['message_id']
    print(r.json())
    print(f'welcome message id: {welcome_msg_id}')
    return welcome_msg_id


def handle_feedback(msg):
    mid = msg['message_id']
    cid = msg['chat']['id']
    r = forward_message(cid, mid, FEEDBACK_CHAT_ID).json()
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
    r = send_message(f'{stored_feedback["chat_id"]}', msg['text'], reply_to=stored_feedback["message_id"])  # notice 'u' before private chat ID
    print(r.json())


def handle_join(msg):
    chat_id = str(msg['chat']['id'])
    from_id = str(msg['from']['id'])
    actor = Profile.get(from_id)

    actor["name"] = msg['from']['first_name'] + msg['from'].get('last_name', '')
    actor["mention"] = msg['from'].get('username', '')
    newcomer_id = str(msg['new_chat_member']['id'])
    if from_id == newcomer_id:
        if len(actor['parents']) == 0:
            # показываем сообщение с кнопкой "поручиться"
            welcome_msg_id = newcomer_show(msg)

            # до одобрения - мьют
            r = mute_member(chat_id, newcomer_id)
            print(r.json())

            # обновляем профиль присоединившегося
            actor['welcome_id'] = welcome_msg_id
            Profile.save(actor)
        else:
            # за пользователя поручились ранее
            r = delete_message(chat_id, actor['welcome_id'])
            print(r.json())
    else:
        # пользователи приглашены другим участником
        print(f'{len(msg["new_chat_members"])} members were invited by {from_id}')    
        for m in msg['new_chat_members']:
            newcomer = Profile.get(m['id'])
            newcomer['parents'].append(from_id)
            Profile.save(newcomer)
            actor['children'].append(m['id'])
            r = unmute_member(chat_id, newcomer['id'])
            print(r.json())

        # обновляем профиль пригласившего
        Profile.save(actor)


def handle_left(msg):
    print(f'handling member leaving')
    member_id = msg["left_chat_member"]["id"]

    # профиль покидающего чат
    leaver = Profile.get(member_id)

    # удаление сообщения с кнопкой
    r = delete_message(msg['chat']['id'], leaver['welcome_id'])
    print(r.json())

    Profile.leaving(leaver)


def handle_button(callback_query):
    # получаем профиль нажавшего кнопку
    actor_id = str(callback_query['from']['id'])
    actor = Profile.get(actor_id)

    callback_data = callback_query['data']
    if callback_data.startswith(BUTTON_VOUCH):
        print(f'vouch button pressed by {actor_id}')

        newcomer_id = callback_data[len(BUTTON_VOUCH):]
        newcomer = Profile.get(newcomer_id)
        if newcomer_id not in actor['children'] and \
            actor_id not in newcomer['parents']:
                newcomer['parents'].append(newcomer_id)
                actor['children'].append(actor_id)
                Profile.save(newcomer)
                Profile.save(actor)
                try:
                    chat_id = str(callback_query['message']['chat']['id'])

                    print('unmute newcomer')
                    r = unmute_member(chat_id, newcomer_id)
                    print(r.json())

                    print('accept join request')
                    r = approve_chat_join_request(chat_id, newcomer_id)
                    print(r.json())

                except:
                    pass
                    

def handle_join_request(update):
    print(f'handle join request')
    chat_id = str(update['message']['chat']['id'])
    from_id = str(update['message']['from']['id'])
    actor = Profile.get(from_id)

    actor["name"] = update['message']['from']['first_name'] + update['message']['from'].get('last_name', '')
    actor["mention"] = update['message']['from'].get('username', '')

    if from_id == str(update['message']['new_chat_member']['id']):
        if len(actor['parents']) == 0:
            # показываем сообщение с кнопкой "поручиться"
            welcome_msg_id = show_request_msg(update)


def handle_graph(_msg):
    cursor = 0
    keys = []
    while True:
        # Scan for keys starting with 'urs-*' in batches of 100
        cursor, batch_keys = r.scan(cursor=cursor, match='urs-*', count=100)
        keys += batch_keys
        # If the cursor is 0, then we've reached the end of the keys
        if cursor == 0:
            break
    # Get the values of all the keys
    values = r.mget(keys)
    # Parse the JSON data from each value
    members = []
    for value in values:
        member = json.loads(value)
        members.append(member)
    png_data = generate_chart(values)
    r = send_graph(png_data, chat_id)
    print(r.json())
