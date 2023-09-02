
import hashlib
import pickle
import sqlite3

import gradio as gr
from gradio.context import Context

from .event import on


DB_PATH = 'oracle.db'

def open_registration(username, password):
    connection = sqlite3.connect(DB_PATH)
    try:
        connection.execute("""
            CREATE TABLE credentials
            (user TEXT PRIMARY KEY, password TEXT)
        """)
    except Exception:
        pass
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

def persist(name, component):
    connection = sqlite3.connect(DB_PATH)
    try:
        connection.execute(f"CREATE TABLE {name} (user TEXT PRIMARY KEY, value TEXT)")
    except Exception:
        pass
    connection.close()

    @on(Context.root_block.load)
    def resume_session(value: component, request: gr.Request) -> component:
        connection = sqlite3.connect(DB_PATH)
        query = connection.execute(
            f"SELECT value FROM {name} WHERE user=?",
            (request.username,),
        )
        saved_value = query.fetchone()
        connection.close()
        new_value = pickle.loads(saved_value[0]) if saved_value else value
        return new_value

    def update_session(value: component, request: gr.Request):
        connection = sqlite3.connect(DB_PATH)
        connection.execute(
            f"INSERT OR REPLACE INTO {name} VALUES (?, ?)",
            (request.username, pickle.dumps(value, 5)),
        )
        connection.commit()
        connection.close()

    if hasattr(component, 'change'):
        on(component.change, update_session)
    else:
        component.change = update_session
    return component
