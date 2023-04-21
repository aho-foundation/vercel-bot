import requests
import json
import os

TOKEN = os.environ.get('BOT_TOKEN')
apiBase = f"https://api.telegram.org/bot{TOKEN}/"


def register_webhook(url):
    r = requests.get(
        apiBase + f'setWebhook?url={url}'
    )
    return r


def delete_message(cid: str, mid: str):
    url = apiBase + f"deleteMessage?chat_id={cid}&message_id={mid}"
    r = requests.post(url)
    return r


def send_message(cid: str, body, reply_to=None, reply_markup=None):
    url = apiBase + f"sendMessage?chat_id={cid}&text={body}"
    if reply_to:
        url += f'&reply_to_message_id={reply_to}'
    if reply_markup:
        reply_markup = json.dumps(reply_markup)
        reply_markup = requests.utils.quote(reply_markup)
        url += f'&reply_markup={reply_markup}'
    r = requests.post(url)
    print(f'{url}')
    return r


# https://core.telegram.org/bots/api#banchatmember
def ban_member(chat_id, user_id, until_date=None):
    url = apiBase + f"banChatMember?chat_id={chat_id}&user_id={user_id}"
    if until_date:
        url += f'&until_data={until_date}'
    r = requests.post(url)
    return r


# https://core.telegram.org/bots/api#unbanchatmember
def unban_member(chat_id, user_id):
    url = apiBase + f"unbanChatMember?chat_id={chat_id}&user_id={user_id}&only_if_banned=1"
    r = requests.post(url)
    return r

# https://core.telegram.org/bots/api#addchatmember
def add_chatmember(chat_id, user_id):
    url = apiBase + f"addChatMember?chat_id={chat_id}&user_id={user_id}"
    r = requests.post(url)
    return r


def forward_message(cid, mid, to_chat_id):
    url = apiBase + f"forwardMessage?chat_id={to_chat_id}" + \
        f"&from_chat_id={cid}&message_id={mid}"
    r = requests.post(url)
    return r


# https://core.telegram.org/bots/api#setchatpermissions
def set_chatpermissions(chat_id, chat_permissions):
    chat_permissions = json.dumps(chat_permissions)
    chat_permissions = requests.utils.quote(chat_permissions)
    url = apiBase + f'setChatPermissions?chat_id={chat_id}' + \
        f'&permissions={chat_permissions}'
    r = requests.post(url)
    return r
