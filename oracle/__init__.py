DB_PATH = 'oracle.db'

def get_device():
    import torch

    if torch.cuda.is_available() and torch.cuda.device_count():
        return 'cuda'
    else:
        return 'cpu'

def log(message, location='.history'):
    from hashlib import md5
    import os

    os.makedirs(location, exist_ok=True)
    key = md5(message.encode(), usedforsecurity=False).hexdigest()[:8]
    with open(f'{location}/{key}.txt', 'w', encoding='utf-8') as f:
        f.write(message)
    return message

def log_error():
    import traceback

    error = traceback.format_exc()
    return log(error, '.history/errors')
