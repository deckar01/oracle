"""
Configure and start the gradio server.
"""

import os

from . import demo
from .session import open_registration


os.environ["GRADIO_ANALYTICS_ENABLED"] = "False"
demo.launch(
    server_port=8080,
    server_name='0.0.0.0',
    show_tips=False,
    quiet=True,
    favicon_path='oracle/gradio/icon.png',
    auth=open_registration,
    auth_message='(or register)',
)
