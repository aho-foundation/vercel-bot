def escape_username(username):
    # Replace any non-ASCII and non-alphanumeric characters with underscores
    return ''.join(c if c.isalnum() or c.isspace() else '-' for c in username)

# generates a mention from standard telegram web json 'from' field
# using HTML markup
def mention(user):
    uid, identity, username = userdata_extract(user)
    identity = escape_username(identity)
    return f'<a href="tg://user?id={uid}">{identity} {username}</a>'


def userdata_extract(user):
    identity = f"{user['first_name']} {user.get('last_name', '')}".strip()
    uid = user['id']
    username = user.get('username', '')
    if username:
        username = f'(@{username})'
    return uid, identity, username

