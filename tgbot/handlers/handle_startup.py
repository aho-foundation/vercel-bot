from tgbot.storage import scan, Profile
from tgbot.api import approve_chat_join_request, kick_member
from tgbot.utils.mention import userdata_extract

# устанавливает соответствие данных
def handle_startup():
    btn_ids, btns = scan(match='btn-*', count=100)
    for btnid in btn_ids:
        # для каждой ранее созданной кнопки
        btnid_str = btnid.decode("utf-8").replace("btn-", "")
        parts = btnid_str.split('-')
        print(parts)
        _, chat_id, member_id = parts
        chat_id = "-" + chat_id
        newcomer = Profile.get(member_id)
        if len(newcomer.get('parents', [])) > 0:
            # принять заявку если её нажимали
            r = approve_chat_join_request(chat_id, member_id)
            print(r)
        elif len(newcomer.get('parents', [])) == 0:
            r = kick_member(chat_id, member_id)
            print(r)
            if r['ok']:
                _, identity, username = userdata_extract(newcomer['result']['user'])
                body = ('Участник %s%s был удалён' if lang == 'ru' else 'Member %s%s was deleted') % (identity, username)
                r = send_message(chat_id, body)
                print(r)