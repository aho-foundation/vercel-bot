import requests
import aiohttp
import json
import os

TOKEN = os.environ.get('BOT_TOKEN')
apiBase = f"https://api.telegram.org/bot{TOKEN}/"


def register_webhook(url):
    r = requests.get(
        apiBase + f'setWebhook?url={url}'
    )
    return r.json()


def delete_message(cid: str, mid: str):
    url = apiBase + f"deleteMessage?chat_id={cid}&message_id={mid}"
    r = requests.post(url)
    return r.json()


# https://core.telegram.org/bots/api#sendmessage
def send_message(cid: str, body, reply_to=None, reply_markup=None):
    url = apiBase + f"sendMessage?chat_id={cid}&text={body}"
    if reply_to:
        url += f'&reply_to_message_id={reply_to}'
    if reply_markup:
        reply_markup = json.dumps(reply_markup)
        reply_markup = requests.utils.quote(reply_markup)
        url += f'&reply_markup={reply_markup}'
    url += f'&parse_mode=HTML'
    r = requests.post(url)
    print(f'{url}')
    return r.json()


# https://core.telegram.org/bots/api#banchatmember
def ban_member(chat_id, user_id, until_date=None):
    url = apiBase + f"banChatMember?chat_id={chat_id}&user_id={user_id}"
    if until_date:
        url += f'&until_data={until_date}'
    r = requests.post(url)
    return r.json()


# https://core.telegram.org/bots/api#unbanchatmember
def unban_member(chat_id, user_id):
    url = apiBase + f"unbanChatMember?chat_id={chat_id}&user_id={user_id}&only_if_banned=1"
    r = requests.post(url)
    return r.json()

# https://core.telegram.org/bots/api#addchatmember
def add_member(chat_id, user_id):
    url = apiBase + f"addChatMember?chat_id={chat_id}&user_id={user_id}"
    r = requests.post(url)
    return r.json()


def forward_message(cid, mid, to_chat_id):
    url = apiBase + f"forwardMessage?chat_id={to_chat_id}" + \
        f"&from_chat_id={cid}&message_id={mid}"
    r = requests.post(url)
    return r.json()


# https://core.telegram.org/bots/api#restrictchatmember
def mute_member(chat_id, member_id):
    chat_permissions = json.dumps({ "can_send_messages": False })
    chat_permissions = requests.utils.quote(chat_permissions)
    url = apiBase + f'restrictChatMember?chat_id={chat_id}' + \
        f'&user_id={member_id}&permissions={chat_permissions}'
    r = requests.post(url)
    return r.json()


# https://core.telegram.org/bots/api#restrictchatmember
def unmute_member(chat_id, member_id):
    chat_permissions = json.dumps({ "can_send_messages": True })
    chat_permissions = requests.utils.quote(chat_permissions)
    url = apiBase + f'restrictChatMember?chat_id={chat_id}' + \
        f'&user_id={member_id}&permissions={chat_permissions}'
    r = requests.post(url)
    return r.json()


# https://core.telegram.org/bots/api#approvechatjoinrequest
def approve_chat_join_request(chat_id, user_id):
    url = apiBase + f"approveChatJoinRequest?chat_id={chat_id}" + \
        f'&user_id={user_id}'
    r = requests.post(url)
    return r.json()


# https://core.telegram.org/bots/api#senddocument
async def send_document(chat_id, data='', filename='chart.svg'):
    url = apiBase + "sendDocument"
    params = { "chat_id": chat_id }
    files = { "document": data }

    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.post(url, params=params, data=filedata) as response:
            if response.status != 200:
                error_text = await response.text()
                print(f"Error sending document: {response.status} - {error_text}")
                return None

            try:
                return await response.json()
            except ValueError as e:
                print(f"Error decoding JSON: {e}")
                return None



# https://core.telegram.org/bots/api#sendphoto
async def send_photo(png_data, chat_id):
    url = apiBase + f"sendPhoto"
    headers = {"Content-Type": "multipart/form-data"}
    files = {"photo": ("chart.png", png_data)}
    params = {"chat_id": chat_id}
    
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.post(url, params=params, data=filedata) as response:
            if response.status != 200:
                print(f"Error sending photo: {response.status}")
                return None

            try:
                return await response.json()
            except ValueError as e:
                print(f"Error decoding JSON: {e}")
                return None


# https://core.telegram.org/bots/api#getchatadministrators
def get_chat_administrators(chat_id):
    url = apiBase + f"getChatAdministrators?chat_id={chat_id}"
    r = requests.get(url)
    return r.json()


# # https://core.telegram.org/bots/api#getchatmember
def get_member(chat_id, member_id):
    url = apiBase + f"getChatMember?chat_id={chat_id}&user_id={member_id}"
    r = requests.get(url)
    return r.json()