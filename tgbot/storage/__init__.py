import redis
from tgbot.storage.profile import Profile as ProfileObj
from tgbot.config import REDIS_URL

# сохраняет сессии и пересылаемые сообщения между перезагрузками
storage = redis.from_url(REDIS_URL)

# хранение необходимой информации о пользователях
Profile = ProfileObj(storage)
