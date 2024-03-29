from sanic import Sanic
from sanic.response import text

from tgbot.config import WEBHOOK, FEEDBACK_CHAT_ID

from tgbot.handlers.handle_feedback import handle_feedback, handle_answer
from tgbot.handlers.handle_members_change import handle_join, handle_left
from tgbot.handlers.handle_join_request import handle_join_request
from tgbot.handlers.handle_default import handle_default
from tgbot.handlers.command_my import handle_command_my
from tgbot.handlers.command_graph import handle_command_graph
from tgbot.handlers.command_ask import handle_command_ask
from tgbot.handlers.callback_vouch import handle_button
from tgbot.handlers.callback_unlink import handle_unlink
from tgbot.handlers.handle_startup import handle_startup
from tgbot.api import register_webhook, send_message


app = Sanic(name="welcomecenter")
app.config.REGISTERED = False


@app.route('/', methods=["GET"])
async def register(req):
    res = 'skipped'
    if not app.config.REGISTERED:
        r = register_webhook(WEBHOOK)
        print(f'\n\t\t\tWEBHOOK REGISTERED:\n{r}')
        app.config.REGISTERED = True
        print(r)
        res = 'ok'
        handle_startup()
    return text(res)
        

@app.post('/')
async def handle(req):
    print(req)
    try:
        update = req.json
        print(update)

        # видимые сообщения
        msg = update.get('message', update.get('edited_message'))
        if msg:
            if 'text' in msg:
                if msg['chat']['id'] == msg['from']['id']:
                    print('private chat message')
                    if msg['text'].startswith('/my'):
                        handle_command_my(msg)
                    elif msg['text'].startswith('/unlink'):
                        handle_unlink(msg)
                    else:
                        handle_feedback(msg)
                elif str(msg['chat']['id']) == FEEDBACK_CHAT_ID:
                    print('feedback chat message')
                    if 'reply_to_message' in msg:
                        handle_answer(msg)
                    elif msg['text'] == '/graph':
                        await handle_command_graph(msg)
                    elif msg['text'].startswith('/ask'):
                        handle_command_ask(msg)
                else:
                    handle_default(msg)
            elif 'new_chat_member' in msg:
                handle_join(msg)
            elif 'left_chat_member' in msg:
                handle_left(msg)
            else:
                print('message without text')

        # кнопки
        elif 'callback_query' in update:
            data = update['callback_query']['data']
            if data.startswith('vouch'):
                handle_button(update['callback_query'])
            elif data.startswith('unlink'):
                handle_unlink(update['callback_query'])

        # заявки
        elif 'chat_join_request' in update:
            print('chat join request')
            handle_join_request(update['chat_join_request'])
        
        # wtf
        else:
            print('unhandled update')

    
    except Exception:
        import traceback
        r = send_message(FEEDBACK_CHAT_ID, f'<pre>\n{traceback.format_exc()}\n</pre>')
        traceback.print_exc()
    return text('ok')
