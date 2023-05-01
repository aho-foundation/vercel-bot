from tgbot.storage import Profile, scan
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

    handle_command_owner_my(msg)

    # генерируем кнопки для всех, за кого поручились
    reply_markup = construct_unlink_buttons(sender)

    if msg['from'].get('language_code', 'ru') == 'ru':
        body = 'Нажмите кнопки ниже, чтобы удалить ваши связи'
    else:
        body = 'Unlink your connections pressing the buttons below'

    r = send_message(from_id, body, reply_markup=reply_markup)
    print(r)


def handle_command_owner_my(msg):
    chat_id = msg['chat']['id']
    r = get_chat_administrators(chat_id)
    print(r)
    owner_id = ''
    for admin in r['result']:
        if admin['status'] == 'creator':
            owner_id = str(admin['user']['id'])
            break
    if owner_id:
        owner = Profile.get(owner_id, msg)
        uids, members = scan()
        for mdata in members:
            m = json.loads(mdata.decode('utf-8'))
            if owner_id in m['parents']:
                if str(m['id']) not in owner['children']:
                    owner['children'].append(str(m['id']))
                    Profile.save(owner)