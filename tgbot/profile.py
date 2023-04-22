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
        self.storage.set(f'usr-{s["id"]}', json.dumps(s))

    def get(self, member_id):
        data = self.storage.get(f'usr-{member_id}')
        if data is None:
            return self.create(member_id)
        else:
            return json.loads(data)

    def leaving(self, s):
        if len(s['parents']) == 0:
            self.storage.delete(f'usr-{s["id"]}')
