from tgbot.api import send_message
from tgbot.config import BUTTON_VOUCH, NEWCOMER_MSG
from tgbot.utils.mention import mention

def show_request_msg(msg):
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
    
    r = send_message(
        msg['chat']['id'],
        NEWCOMER_MSG + mention(msg['from']),   
        reply_to=msg.get('message_id', ''),
        reply_markup=reply_markup
    )
    btn_msg_id = r['result']['message_id']
    print(f'request message id: {btn_msg_id}')
    return btn_msg_id
