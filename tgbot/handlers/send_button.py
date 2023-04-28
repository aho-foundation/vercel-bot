from tgbot.api import send_message, send_photo, get_userphotos
from tgbot.utils.mention import mention
from tgbot.storage import storage

def show_request_msg(msg):
    chat_id = str(msg['chat']['id'])
    from_id = str(msg['from']['id'])
    lang = msg['from'].get('language_code', 'ru')
    reply_markup = {
        "inline_keyboard": [
            [
                {
                    "text": 'Моё одобрение' if lang == 'ru' else 'My connection', 
                    "callback_data": 'vouch' + from_id
                }
            ]
        ]
    }
    newcomer_message = "Нажмите, чтобы одобрить заявку " if lang == 'ru' \
        else "There is a newcomer, press the button if you are connected with "
    r = get_userphotos(user_id=from_id)
    print(r)
    if r['ok'] and r['result']['total_count'] > 0:
        file_id = r['result']['photos'][0][0]['file_id']
        r = send_photo(
            chat_id,
            file_id,
            caption=newcomer_message + mention(msg['from']),
            reply_to=msg.get('message_id', ''),
            reply_markup=reply_markup
        )
    else:
        r = send_photo(
            chat_id,
            newcomer_message + mention(msg['from']),   
            reply_to=msg.get('message_id', ''),
            reply_markup=reply_markup
        )
    print(r)
    if 'message_id' in r:
        # удаляем предыдущее сообщение с кнопкой в этом чате
        prevbtn = storage.get(f'btn-{chat_id}-{from_id}')
        if prevbtn:
            r = delete_message(chat_id, prevbtn)
            print(r)
        # создаём новое
        newbtn = r['message_id']
        print(f'button message id: {newbtn}')
        storage.set(f'btn-{chat_id}-{from_id}', newbtn)
