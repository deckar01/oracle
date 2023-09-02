def get():
    import torch

    if torch.cuda.is_available() and torch.cuda.device_count():
        return 'cuda'
    else:
        return 'cpu'
