LETTERS = 'qwertyuiopasdfghjklzxcvbnm'


def check_password(password: str) -> bool:
    c, has_digit = 0, False
    for symbol in password:
        c += 1
        if not symbol.isdigit() and symbol not in LETTERS:
            return False
        if symbol.isdigit():
            has_digit = True
    if c < 8 or not has_digit:
        return False
    return True
