import os
import hashlib
import sqlite3

from oracle import DB_PATH
from oracle.gradio.gui import demo


def open_registration(username, password):
    connection = sqlite3.connect(DB_PATH)
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    query = connection.execute(
        "SELECT password FROM credentials WHERE user=?",
        (username,),
    )
    saved_hash = query.fetchone()
    if not saved_hash:
        connection.execute(
            "INSERT OR REPLACE INTO credentials VALUES (?, ?)",
            (username, password_hash),
        )
        connection.commit()
        saved_hash = password_hash
    else:
        saved_hash = saved_hash[0]
    connection.close()
    return password_hash == saved_hash

if __name__ == '__main__':
    connection = sqlite3.connect(DB_PATH)
    try: connection.execute("CREATE TABLE credentials (user TEXT PRIMARY KEY, password TEXT)")
    except: pass
    connection.close()

    os.environ["GRADIO_ANALYTICS_ENABLED"] = "False"
    demo.launch(
        server_port=8080,
        server_name='0.0.0.0',
        quiet=True,
        favicon_path='oracle/gradio/icon.png',
        auth=open_registration,
        auth_message='(or register)',
    )
