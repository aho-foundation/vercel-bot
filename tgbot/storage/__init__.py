import redis
from tgbot.storage.profile import Profile as ProfileObj
from tgbot.config import REDIS_URL
import json


# сохраняет сессии, айди кнопок в чатах для удаления и пересылаемые сообщения между перезагрузками
storage = redis.from_url(REDIS_URL)

# хранение необходимой информации о пользователях
Profile = ProfileObj(storage)

# достаёт из хранилища jsonы по маске и количеству
def scan(match='usr-*', count=100):
    cursor = 0
    keys = []
    r = storage
    while True:
        # Scan for keys starting with <match> in batches of <count>
        cursor, batch_keys = r.scan(cursor=cursor, match=match, count=count)
        keys += batch_keys
        # If the cursor is 0, then we've reached the end of the keys
        if cursor == 0:
            break
    # Get the values of all the keys
    values = r.mget(keys)
    # Parse the JSON data from each value
    items = []
    for value in values:
        value_str = value.decode('utf-8')
        i = json.loads(value_str)
        items.append(i)
    print(f'scan found {len(items)} items')

    return keys, items