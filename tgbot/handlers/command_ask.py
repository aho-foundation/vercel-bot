from tgbot.storage import Profile
from tgbot.handlers.send_button import show_request_msg
from tgbot.api import get_member

def handle_command_ask(msg):
    print(f'handling request resend')
    cmd, chat_id, member_id = msg['text'].split(' ')
    chat_id = chat_id.replace('-', '-100')
    r = get_member(chat_id, member_id)
    print(r)
    m = {}
    m['from'] = r['result']['user']
    m['chat'] = { 'id': chat_id }
    show_request_msg(m)