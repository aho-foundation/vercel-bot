import os


REDIS_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379'
WEBHOOK = os.environ.get('VERCEL_URL') or 'http://localhost:8000'
WELCOME_MSG = os.environ.get('WELCOME_MSG') or 'Welcome! Press the button'
BUTTON_OK = os.environ.get('BUTTON_OK') or 'Ok'
BUTTON_OK2 = os.environ.get('BUTTON_OK2') or 'I see'
BUTTON_NO = os.environ.get('BUTTON_NO') or 'No'

CHAT_ID = os.environ.get('CHAT_ID').replace("-", "-100")
FEEDBACK_CHAT_ID = os.environ.get('FEEDBACK_CHAT_ID').replace("-", "-100")