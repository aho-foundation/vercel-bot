from tgbot.api import send_message, delete_message
from tgbot.storage import Profile

# remove link of callback sender 
# from member vouched before
def handle_unlink(callback_query):
    print('handle unlink button pressed, private chat only')
    
    from_id = str(callback_query['from']['id'])
    reply_msg_id = callback_query['message']['message_id']

    actor = Profile.get(from_id, callback_query)
    actor['parents'].remove(from_id)
    
    # удаляем старое сообщение с кнопками
    r = delete_message(from_id, reply_msg_id)
    print(r)

    # если ещё есть связи - посылаем новое сообщение
    if len(actor['parents']) > 0:
        body = construct_unlink_buttons(actor)
        r = send_message(from_id, body)
        print(r)