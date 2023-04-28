from tgbot.utils.graph import generate_chart
from tgbot.api import send_document
from tgbot.storage import storage, scan
import json


async def handle_command_graph(msg):
    usr_ids, members = scan(match='usr-*', count=100)
    data = generate_chart(members)
    if data:
        r = await send_document(msg['chat']['id'], data, 'chart.svg')
        print(r)
