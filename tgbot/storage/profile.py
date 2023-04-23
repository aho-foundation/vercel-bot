import json


class Profile:

    def __init__(self, storage):
        self.storage = storage

    def create(self, member_id, msg=None):
        s = {
            "id": member_id,
            "request_msg_id": 0,
            "parents": [],
            "children": [],
            "chats": []
        }

        if msg.get('from'):
            sender = msg.get('from')
            s["mention"] = sender.get('username')
            s["name"] = f"{sender['first_name']} {sender.get('last_name', '')}".strip()

        if msg.get('chat'):
            chat_id = str(msg['chat']['id'])
            if chat_id not in s['chats']:
                s["chats"].append(chat_id)

        self.storage.set(f'usr-{member_id}', json.dumps(s))
        return s

    def save(self, s):
        self.storage.set(f'usr-{s["id"]}', json.dumps(s))

    def get(self, member_id, msg=None):
        data = self.storage.get(f'usr-{member_id}')
        if data is None:
            r = self.create(member_id, msg)
        else:
            r = json.loads(data)
        return r

    def leaving(self, s):
        if len(s['parents']) == 0:
            self.storage.delete(f'usr-{s["id"]}')
