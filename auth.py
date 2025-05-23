import bcrypt

def hash_password(password):
    if not password:
        raise ValueError("Password cannot be empty.")
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def check_password(password, hashed):
    if not password or not hashed:
        return False
    return bcrypt.checkpw(password.encode(), hashed.encode())
