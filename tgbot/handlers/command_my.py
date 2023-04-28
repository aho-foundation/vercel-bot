from tgbot.storage import Profile
from tgbot.api import get_member, send_message
from tgbot.utils.mention import userdata_extract


def construct_unlink_buttons(actor):
    buttons = []
    for vouch in actor['children']:
        for chat_id in actor['chats']:
            r = get_member(chat_id, vouch)
            member = r['result']['user']
            uid, identity, username = userdata_extract(member)
            buttons.append({
                'text': f'{identity} {username}',
                'callback_data': 'unlink' + vouch
            })
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