from tgbot.config import WEBHOOK, FEEDBACK_CHAT_ID # init storage there
from tgbot.handlers import handle_feedback, handle_answer, \
    handle_join, handle_left, handle_button, handle_join_request, \
        handle_graph
from tgbot.api import register_webhook
from sanic import Sanic
from sanic.response import text


app = Sanic()
app.config.REGISTERED = False


@app.route('/', methods=["GET"])
async def register(req):
    if not app.config.REGISTERED:
        r = register_webhook(WEBHOOK)
        print(f'\n\t\t\tWEBHOOK REGISTERED:\n{r.json()}')
        app.config.REGISTERED = True
        print(r.json())
        return text('ok')
    return text('skipped')


@app.post('/')
async def handle(req):
    print(req)
    try:
        update = req.json
        print(update)
        if 'message' in update:
            msg = update.get('message', update.get('edited_message'))
            if msg['chat']['type'] == 'private':
                handle_feedback(msg)
            elif str(msg['chat']['id']) == FEEDBACK_CHAT_ID:
                if 'reply_to_message' in msg:
                    handle_answer(msg)
                elif 'text' in msg and msg['text'] == '/graph':
                    handle_graph(msg)
            else:
                if 'new_chat_member' in msg:
                    handle_join(msg)
                elif 'left_chat_member' in msg:
                    handle_left(msg)
        elif 'callback_query' in update:
            handle_button(update['callback_query'])
        elif 'chat_join_request' in update:
            print('chat join request')
            handle_join_request(update)
    except Exception:
        import traceback
        traceback.print_exc()
    return text('ok')
