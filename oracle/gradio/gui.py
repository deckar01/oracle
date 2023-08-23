import gradio as gr

from contexts import CONTEXTS
from oracle.engine import chat
from oracle.gradio.config import STYLES
from oracle.gradio.utils import *


with gr.Blocks(title='Oracle', css='oracle/gradio/gui.css').queue() as demo:
    # View

    chatbot = gr.Chatbot(elem_id='chatbot', show_label=False)

    with gr.Accordion('Settings', open=False, elem_id='settings'):
        default_context = CONTEXTS['None']
        motive = gr.Dropdown(
            label='Motivation',
            value=default_context.motive,
            choices=[default_context.motive],
            allow_custom_value=True,
        )
        source = gr.Dropdown(
            label='Source',
            choices=list(CONTEXTS.keys()),
            value=default_context.name,
            allow_custom_value=False,
        )
        style = gr.Dropdown(
            label='Response Style',
            choices=STYLES,
            allow_custom_value=True,
        )

    with gr.Row():
        message = gr.Textbox(
            placeholder='Message',
            lines=3,
            show_label=False,
            container=False,
            scale=1,
        )
        send = gr.Button('Send', variant='primary', scale=0)
        stop = gr.Button('Stop', variant='stop', visible=False, scale=0)

    # Controller

    def chat_handler(source, motive, style, message, chatbot):
        log = ''
        response = ''
        preview = [message, None]
        chatbot.append(preview)
        yield locked(), chatbot, hide(), show()

        for change in chat(message, motive, source, style):
            response = change.get('response', '')
            status = change.get('status', '')
            log = change.get('log', '')

            preview[1] = response
            if status: preview[1] += note(status)
            if log: preview[1] += fold(log)

            yield locked(), chatbot, hide(), show()

        preview[1] = response
        if log: preview[1] += fold(log)
        if not status: message = ''

        yield unlocked(value=message), chatbot, show(), hide()

    chat_thread = send.click(
        chat_handler,
        inputs=[source, motive, style, message, chatbot],
        outputs=[message, chatbot, send, stop],
    )

    stop.click(
        lambda: (unlocked(), show(), hide()),
        outputs=[message, send, stop],
        cancels=[chat_thread],
    )

    source.change(
        lambda source: gr.update(
            value=CONTEXTS[source].motive,
            choices=[CONTEXTS[source].motive],
        ),
        inputs=source,
        outputs=motive,
    )
