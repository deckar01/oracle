import inspect

import gradio as gr
from gradio.components.base import IOComponent


def on(event, fn=None, **kwargs):
    def wrapper(fn):
        annotations = inspect.get_annotations(fn)
        event_options = dict(on.default)
        event_options['outputs'] = annotations.pop('return', None)
        event_options['inputs'] = [
            input for input in annotations.values()
            if isinstance(input, IOComponent)
        ]
        event_options.update(kwargs)
        return event(fn, **event_options)
    return wrapper(fn) if fn else wrapper

on.default = {}

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
