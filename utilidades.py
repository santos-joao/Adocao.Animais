import bcrypt

def hash_senha(senha):
    salt = bcrypt.gensalt()
    hashed_senha = bcrypt.hashpw(senha.encode('utf-8'), salt)
    return hashed_senha

def verify_senha(senha, hashed_senha):
    if isinstance(hashed_senha, str):
        hashed_senha = hashed_senha.encode('utf-8')
    return bcrypt.checkpw(senha.encode('utf-8'), hashed_senha)