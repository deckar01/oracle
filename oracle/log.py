import hashlib
import os
import traceback


def write(message, location='.history'):
    os.makedirs(location, exist_ok=True)
    hash = hashlib.md5(message.encode(), usedforsecurity=False)
    key = hash.hexdigest()[:8]
    with open(f'{location}/{key}.txt', 'w', encoding='utf-8') as f:
        f.write(message)
    return message

def error():
    error = traceback.format_exc()
    print(error)
    return write(error, '.history/errors')
