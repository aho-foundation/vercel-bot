from tgbot.api import send_message, forward_message, delete_message, \
    ban_member, unban_member, set_chatpermissions
from tgbot.config import FEEDBACK_CHAT_ID, WELCOME_MSG, BUTTON_NO, \
    BUTTON_OK, CHAT_ID, REDIS_URL
import json
import redis
from tgbot.profile import Profile as ProfileObj


# сохраняет сессии и пересылаемые сообщения между перезагрузками
storage = redis.from_url(REDIS_URL)

# хранение необходимой информации о пользователях
Profile = ProfileObj(storage)


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
    member_id = str(msg['new_chat_member']['id'])

    if from_id == member_id:
        newcomer = Profile.get(member_id)

        print(f'new self-joined member {member_id}')
        reply_markup = {
            "inline_keyboard": [
                [
                    {"text": BUTTON_NO, "callback_data": BUTTON_NO},
                    {"text": BUTTON_OK, "callback_data": BUTTON_OK},
                    {"text": BUTTON_VOUCH, "callback_data": BUTTON_VOUCH}
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
        newcomer["newcomer"] = True
        newcomer["welcome_id"] = welcome_msg_id
        perms = {
            "can_send_messages": False
        }
        r = set_chatpermissions(CHAT_ID, perms)
        print(r.json())
        # обновляем профиль новичка
        Profile.save(newcomer)

    elif 'new_chat_members' in msg:
        # кто-то пригласил новых участников
        print(f'{len(msg["new_chat_members"])} members were invited by {from_id}')
        # получаем его профиль
        inviter = Profile.get(from_id)
        
        for m in msg['new_chat_members']:
            newcomer = Profile.get(m['id'])
            newcomer['vouched_by'].append(from_id)
            Profile.save(newcomer)

            inviter['vouched_for'].append(m['id'])
        # обновляем профиль пригласившего
        Profile.save(inviter)


def handle_left(msg):
    print(f'handling member leaving')

    member_id = msg["left_chat_member"]["id"]

    # профиль покидающего чат
    leaver = Profile.get(member_id)

    r = delete_message(CHAT_ID, leaver['welcome_id'])
    print(r.json())

    Profile.leaving(leaver)


def handle_button(callback_query):
    if 'reply_to_message' not in callback_query['message']:
        # удаляет сообщение с кнопкой, если оно уже ни на что не отвечает
        r = delete_message(CHAT_ID, callback_query['message'])
        print(r.json())
    else:
        member_id = str(callback_query['from']['id'])
        callback_data = callback_query['data']
        welcomed_member_id = str(callback_query['message']['reply_to_message']['from']['id'])
        welcome_msg_id = str(callback_query['message']['message_id'])
        enter_msg_id = str(callback_query['message']['reply_to_message']['message_id'])
        
        # получаем профиль нажавшего кнопку
        actor = Profile.get(member_id)
        
        if welcomed_member_id == member_id:
            print(f'callback_query in {CHAT_ID}')
            
            if callback_data == BUTTON_NO:
                print('wrong answer, cleanup')
                r = delete_message(CHAT_ID, enter_msg_id)
                print(r.json())
                r = delete_message(CHAT_ID, welcome_msg_id)
                print(r.json())
                print('ban member')
                r = ban_member(CHAT_ID, member_id)
                print(r.json())

                # обработка профиля заблокированного пользователя
                Profile.leaving(actor)

            elif callback_data == BUTTON_OK:
                print('proper answer, cleanup')
                r = delete_message(CHAT_ID, welcome_msg_id)
                print(r.json())
                actor['newcomer'] = False

                r = delete_message(CHAT_ID, author["welcome_id"])
                print(r.json())

                r = set_chatpermissions(CHAT_ID, { "can_send_messages": True })
                print(r.json())

                # обновление профиля нажавшего правильную кнопку
                Profile.save(actor)
                
        elif callback_data == BUTTON_VOUCH:
            # это кнопка поручения
            print(f'vouch button pressed by {member_id}')
            newcomer = Profile.get(welcomed_member_id)
            if welcomed_member_id not in inviter['vouched_for'] and \
                member_id not in newcomer['vouched_by']:
                newcomer['vouched_by'].append(welcomed_member_id)
                actor['vouched_for'].append(member_id)
                Profile.save(newcomer)
                Profile.save(actor)
                print('vouch success, unban member')
                r = unban_member(CHAT_ID, member_id)
                print(r.json())
                
