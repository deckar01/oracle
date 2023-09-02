import inspect

import gradio as gr
from gradio.components.base import IOComponent


def on(event, fn=None, queue=False, **kwargs):
    def wrapper(fn):
        sig = inspect.get_annotations(fn)
        outputs = sig.pop('return', None)
        inputs = list(
            input for input in sig.values()
            if isinstance(input, IOComponent)
        )
        return event(
            fn,
            inputs=inputs,
            outputs=outputs,
            queue=queue,
            **kwargs,
        )
    return wrapper(fn) if fn else wrapper

def after(event, *args, **kwargs):
    return on(event.then, *args, **kwargs)

def locked(**kwargs):
    return gr.update(**kwargs, interactive=False)

def unlocked(**kwargs):
    return gr.update(**kwargs, interactive=True)

def show():
    return gr.update(visible=True)

def hide():
    return gr.update(visible=False)

def note(status):
    return f'<span class="status">{status}</span>'

def fold(summary, details):
    if isinstance(details, dict):
        content = '\n\n'.join(
            fold(name, detail)
            for name, detail in details.items()
        )
    else:
        details = details.replace('```', '\\`\\`\\`')
        content = f'```\n{details}\n```'
    return f'<details><summary>{summary}</summary>\n\n{content}\n\n</details>'
