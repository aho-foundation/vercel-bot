from tgbot.api import send_message, delete_message
from tgbot.handlers.command_my import handle_command_my
from tgbot.storage import Profile

# remove link of callback sender 
# from member vouched before
def handle_unlink(callback_query):
    print('handle unlink button pressed, private chat only')
    
    from_id = str(callback_query['from']['id'])
    linked_id = str(callback_query['data'].replace('unlink', ''))

    # удаляем связь с потомком
    actor = Profile.get(from_id, callback_query)
    actor['children'].remove(linked_id)
    Profile.save(actor)

    # удаляем связь с предком
    linked = Profile.get(linked_id)
    linked['parents'].remove(from_id)
    Profile.save(linked)

    # удаляем старое сообщение с кнопками
    reply_msg_id = callback_query['message']['message_id']
    r = delete_message(from_id, reply_msg_id)
    print(r)
     
    # если ещё есть связи - посылаем новое сообщение                                                    
    if len(actor['children']) > 0:
        handle_command_my(callback_query)

    # если больше никто не поручился - мьютим
    if len(linked['parents']) == 0:
        for chat_id in linked['chats']:
            mute_member(chat_id, linked_id)