import os


WEBHOOK = os.environ.get('VERCEL_URL') or 'http://localhost:8000'
REDIS_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379'
NEWCOMER_MSG = os.environ.get('WELCOME_MSG') or "There is a newcomer, press the button if you are connected"
BUTTON_VOUCH = os.environ.get('BUTTON_VOUCH') or 'My connection!'
FEEDBACK_CHAT_ID = os.environ.get('FEEDBACK_CHAT_ID').replace("-", "-100")