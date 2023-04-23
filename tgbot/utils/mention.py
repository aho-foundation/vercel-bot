# generates a mention from standard telegram web json 'from' field
# using HTML markup
def mention(user):
    identity = f"{user['first_name']} {user.get('last_name', '')}".strip()
    uid = user['id']
    username = user.get('username', '')
    if username:
        username = f'(@{username})'
    return f'<a href="tg://user?id={uid}"><b>{identity}</b></a>{username}'
