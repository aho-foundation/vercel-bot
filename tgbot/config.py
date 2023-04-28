import os


WEBHOOK = os.environ.get('VERCEL_URL') or 'http://localhost:8000'
REDIS_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379'
FEEDBACK_CHAT_ID = os.environ.get('FEEDBACK_CHAT_ID').replace("-", "-100")