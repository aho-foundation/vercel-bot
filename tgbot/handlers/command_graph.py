from tgbot.utils.graph import generate_chart
from tgbot.api import send_document
from tgbot.storage import storage
import json


async def handle_command_graph(msg):
    cursor = 0
    keys = []
    r = storage
    while True:
        # Scan for keys starting with 'usr-*' in batches of 100
        cursor, batch_keys = r.scan(cursor=cursor, match='usr-*', count=100)
        keys += batch_keys
        # If the cursor is 0, then we've reached the end of the keys
        if cursor == 0:
            break
    # Get the values of all the keys
    values = r.mget(keys)
    # Parse the JSON data from each value
    members = []
    for value in values:
        value_str = value.decode('utf-8')
        member = json.loads(value_str)
        members.append(member)
    print(f'found {len(members)} members')
    data = generate_chart(members)
    r = await send_document(msg['chat']['id'], data, 'chart.svg')
    print(r)
