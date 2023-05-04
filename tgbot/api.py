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
    url = f"sendMessage?chat_id={cid}&text={body}"
    if reply_to:
        url += f'&reply_to_message_id={reply_to}'
    if reply_markup:
        reply_markup = json.dumps(reply_markup)
        reply_markup = requests.utils.quote(reply_markup)
        url += f'&reply_markup={reply_markup}'
    url += f'&parse_mode=html'
    print(url)
    r = requests.post(apiBase + url)
    return r.json()

# https://core.telegram.org/bots/api#sendphoto
def send_photo(cid: str, file_id: str, caption="", reply_to=None, reply_markup=None):
    url = f"sendPhoto?chat_id={cid}&photo={file_id}&caption={caption}"
    if reply_to:
        url += f'&reply_to_message_id={reply_to}'
    if reply_markup:
        reply_markup = json.dumps(reply_markup)
        reply_markup = requests.utils.quote(reply_markup)
        url += f'&reply_markup={reply_markup}'
    url += f'&parse_mode=html'
    print(url)
    r = requests.post(apiBase + url)
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
        f'&user_id={member_id}&permissions={chat_permissions}' + \
        f'&use_independent_chat_permissions=1'
    r = requests.post(url)
    return r.json()


# https://core.telegram.org/bots/api#restrictchatmember
def unmute_member(chat_id, member_id, chat_permissions=None):
    if not chat_permissions:
        chat_permissions = json.dumps({ 
            "can_send_messages": True,
            "can_send_photos": True,
            "can_send_other_messages": True,
            "can_send_polls": True,
            "can_add_web_page_previews": True,
            "can_send_audios": True,
            "can_invite_users": True,
            "can_send_voice_notes": True,
            "can_send_video_notes": True,
            "can_send_videos": True,
            "can_send_documents": True
        })
    chat_permissions = requests.utils.quote(chat_permissions)
    url = apiBase + f'restrictChatMember?chat_id={chat_id}' + \
        f'&user_id={member_id}&permissions={chat_permissions}' + \
        f'&use_independent_chat_permissions=1'
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
    filedata = aiohttp.FormData()
    filedata.add_field('document', data, filename=filename)

    async with aiohttp.ClientSession() as session:
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


# https://core.telegram.org/bots/api#getchatadministrators
def get_chat_administrators(chat_id):
    url = apiBase + f"getChatAdministrators?chat_id={chat_id}"
    r = requests.get(url)
    return r.json()


# https://core.telegram.org/bots/api#getchatmember
def get_member(chat_id, member_id):
    url = apiBase + f"getChatMember?chat_id={chat_id}&user_id={member_id}"
    r = requests.get(url)
    return r.json()


# https://core.telegram.org/bots/api#getuserprofilephotos
def get_userphotos(user_id):
    url = apiBase + f"getUserProfilePhotos?user_id={user_id}"
    r = requests.get(url)
    return r.json()

# https://core.telegram.org/bots/api#editmessagereplymarkup
def edit_replymarkup(cid, mid, reply_markup):
    reply_markup = json.dumps(reply_markup)
    reply_markup = requests.utils.quote(reply_markup)
    url = f"editMessageReplyMarkup?chat_id={cid}&message_id={mid}&reply_markup={reply_markup}"
    r = requests.post(apiBase + url)
    return r.json()


# https://core.telegram.org/bots/api#getchat
def get_chat(cid):
    url = apiBase + f"getChat?chat_id={cid}"
    r = requests.get(url)
    return r.json()


# https://core.telegram.org/bots/api#banchatmember
def kick_member(chat_id, member_id):
    url = f"banChatSenderChat?chat_id={cid}&user_id={member_id}"
    r = requests.post(apiBase + url)
    print(r.json())
    url = f"unbanChatSenderChat?chat_id={cid}&user_id={member_id}&only_if_banned=1"
    r = requests.post(apiBase + url)
    return r.json()