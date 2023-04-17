from tgbot.config import WEBHOOK, FEEDBACK_CHAT_ID, CHAT_ID # init storage there
from tgbot.handlers import handle_feedback, handle_answer, handle_welcome, \
    handle_left, handle_text, handle_button
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
                handle_answer(msg)
            elif str(msg['chat']['id']) == CHAT_ID:
                if 'new_chat_member' in msg:
                    handle_welcome(msg)
                elif 'left_chat_member' in msg:
                    handle_left(msg)
                elif 'text' in msg:
                    handle_text(msg)
        if 'callback_query' in update:
            callback_query = update['callback_query']
            chat_id = str(callback_query['message']['chat']['id'])
            if chat_id == CHAT_ID:
                handle_button(callback_query)
    except Exception:
        import traceback
        traceback.print_exc()
    return text('ok')
