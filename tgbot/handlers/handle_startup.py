from tgbot.storage import scan, Profile

# устанавливает соответствие данных
def handle_startup():
    btn_ids, btns = scan(match='btn-*', count=100)
    for btnid in btn_ids:
        # для каждой ранее созданной кнопки
        try:
            btnid_str = btnid.decode("utf-8") 
            chat_id, member_id = btnid_str[3:].split('-')
            
            newcomer = Profile.get(member_id)
            if len(newcomer.get('parents', [])) > 0:
                # принять заявку если её нажимали
                r = approve_chat_join_request(chat_id, member_id)
                print(r)
        except:
            print(f'error {btnid}')