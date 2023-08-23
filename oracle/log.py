from hashlib import md5

def log(location, message):
    key = md5(message.encode(), usedforsecurity=False).hexdigest()[:8]
    with open(f'{location}/{key}.txt', 'w', encoding='utf-8') as f:
        f.write(message)
