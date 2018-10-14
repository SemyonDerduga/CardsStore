from collections import namedtuple

User = namedtuple('User', ['username', 'password', 'balance', 'cards'])

user_map = {
    user.username: user for user in [
        User('sam', '1',  1000, ['python']),
        User('jack', 'password', 500, ['python']),
    ]
}
