import gradio as gr


theme=gr.themes.Default(
    primary_hue=gr.themes.colors.blue,
    radius_size='none',
    spacing_size='sm',
).set(
    layout_gap='0',
    form_gap_width='0',
    input_background_fill='*background_fill_primary',
    input_background_fill_dark='*background_fill_primary',
    block_shadow='none',
    block_shadow_dark='none',
)

css='oracle/gradio/theme.css'

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
