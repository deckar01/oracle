import inspect
from uuid import uuid4

import gradio as gr
from gradio.context import Context
from gradio.events import Changeable


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

user_sessions = {}

def get_session_id(request):
    session_id = user_sessions.get(request.username, None)
    if not session_id:
        session_id = uuid4()
    if request.username:
        user_sessions[request.username] = session_id
    return session_id

def persist(component):
    sessions = {}
    @on(Context.root_block.load)
    def resume_session(value: component, request: gr.Request) -> component:
        return sessions.get(get_session_id(request), value)
    def update_session(value: component, request: gr.Request):
        sessions[get_session_id(request)] = value

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
