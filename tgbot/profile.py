import json


class Profile:

    def __init__(self, storage):
        self.storage = storage

    def create(self, member_id):
        s = {
            "id": member_id,
            "name": "newcomer",
            "mention": "",
            "welcome_id": 0,
            "parents": [],
            "children": []
        }
        self.storage.set(f'usr-{member_id}', json.dumps(s))
        return s

    def save(self, s):
        self.storage.set(f'usr-{member_id}', json.dumps(s))

    def get(self, member_id):
        return json.loads(self.storage.get(f'usr-{member_id}')) or self.create_session(member_id)

    def leaving(self, s):
        if len(s['parents']) == 0:
            self.storage.delete(f'usr-{s["id"]}')
