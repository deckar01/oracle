import inspect
import sqlite3
import pickle

import gradio as gr
from gradio.context import Context
from gradio.events import Changeable

from oracle import DB_PATH


def locked(**kwargs):
    return gr.update(**kwargs, interactive=False)

def unlocked(**kwargs):
    return gr.update(**kwargs, interactive=True)

def on(event, fn=None, **kwargs):
    def wrapper(fn):
        sig = inspect.get_annotations(fn)
        outputs = sig.pop('return', None)
        inputs = list(
            input for input in sig.values()
            if input not in (gr.Request, gr.OAuthProfile, gr.Progress)
        )
        return event(fn, inputs=inputs, outputs=outputs, **kwargs)
    if fn:
        return wrapper(fn)
    else:
        return wrapper

def persist(name, component):
    connection = sqlite3.connect(DB_PATH)
    try: connection.execute(f"CREATE TABLE {name} (user TEXT PRIMARY KEY, value TEXT)")
    except: pass
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
        return pickle.loads(saved_value[0]) if saved_value else value

    def update_session(value: component, request: gr.Request):
        connection = sqlite3.connect(DB_PATH)
        query = connection.execute(
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

def show():
    return gr.update(visible=True)

def hide():
    return gr.update(visible=False)

def note(status):
    return f'<span class="status">{status}</span>'

def fold(details, summary='View Context'):
    details = details.replace('```', '\\`\\`\\`')
    return f'''
<details>
<summary>{summary}</summary>

```
{details}
```

</details>
    '''
