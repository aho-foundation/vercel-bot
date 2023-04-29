from tgbot.api import send_message, delete_message, kick_member
from tgbot.handlers.command_my import handle_command_my
from tgbot.utils.mention import userdata_extract
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

    # если больше никто не поручился - kick out
    if len(linked['parents']) == 0:
        lang = callback_query['from'].get('language_code', 'ru')
        for chat_id in linked['chats']:
            r = kick_member(chat_id, linked_id)
            print(r)
            if r['ok']:
                _, identity, username = userdata_extract(linked['result']['user'])
                body = ('Участник %s%s был удалён' if lang == 'ru' else 'Member %s%s was deleted') % (identity, username)
                r = send_message(chat_id, body)
                print(r)