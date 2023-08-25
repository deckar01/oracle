import gradio as gr


def locked(**kwargs):
    return gr.update(**kwargs, interactive=False)

def unlocked(**kwargs):
    return gr.update(**kwargs, interactive=True)

def guard(op):
    def wrapper(*args, **kwargs):
        yield locked()
        yield op(*args, **kwargs)
        yield unlocked()
    return wrapper

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
