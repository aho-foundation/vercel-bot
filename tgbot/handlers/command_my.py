from tgbot.storage import Profile
from tgbot.api import get_member

def construct_unlink_buttons(actor):
    buttons = []
    for vouch in actor['children']:
        vouch_added = False
        for chat_id in actor['chats']:
            if not vouch_added:
                r = get_member(chat_id, vouch)
                member = r.get('result')
                if member:
                    try:
                        buttons.append({
                            'text': mention(r['result']),
                            'callback_data': 'unlink' + vouch
                        })
                        vouch_added = True
                    except:
                        print('member result error')
                        print(member)
                else:
                    print(r)
    return { "inline_keyboard": [ buttons, ] }

def handle_command_my(msg):
    print(f'handle my command')
    from_id = str(msg['from']['id'])
    sender = Profile.get(from_id, msg)

    # генерируем кнопки для всех, за кого поручились
    reply_markup = construct_unlink_buttons(sender)

    if msg['from'].get('language_code', 'ru') == 'ru':
        body = 'Нажмите кнопки ниже, чтобы удалить ваши связи'
    else:
        body = 'Unlink your connections pressing the buttons below'

    r = send_message(from_id, body, reply_markup=reply_markup)
    print(r)