def username_exists(username: str) -> bool:
    pass

def add_user(username: str, password: str) -> bool:


def password_strong(password: str) -> bool:
    if len(password) < 8:
        return False

    upper_letters = 0
    letters = 0
    digits = 0

    for char in password:
        if char.isdigit():
            digits += 1
        else:
            if char.isupper():
                upper_letters += 1
            letters += 1
    return upper_letters >= 1 and letters >= 1 and digits >= 1

def create_user(username: str, password: str) -> bool:
    if username_exists(username) or not password_strong(password):
        pass
    else:
        add_user(username, password)

