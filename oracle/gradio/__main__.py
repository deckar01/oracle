import os
import hashlib
from oracle.gradio.gui import demo


credentials = {}

def open_registration(username, password):
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    saved_hash = credentials.get(username, password_hash)
    credentials[username] = saved_hash
    return password_hash == saved_hash

if __name__ == '__main__':
    os.environ["GRADIO_ANALYTICS_ENABLED"] = "False"
    demo.launch(
        server_port=8080,
        server_name='0.0.0.0',
        quiet=True,
        favicon_path='oracle/gradio/icon.png',
        auth=open_registration,
        auth_message='(or register)',
    )
