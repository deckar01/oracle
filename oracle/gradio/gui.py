import gradio as gr

from oracle.session import ChatSession
from .config import STYLES
from .utils import *


with gr.Blocks(title='Oracle', css='oracle/gradio/gui.css').queue() as demo:
    # Model

    session_state = gr.State(ChatSession)

    # View

    chat_log = gr.Chatbot(elem_id='chatbot', show_label=False)

    with gr.Accordion('Settings', open=False, elem_id='settings'):
        model_input = gr.Dropdown(label='Chat Model')
        context_input = gr.Dropdown(label='Source')
        motive_input = gr.Textbox(label='Motivation')
        style_input = gr.Dropdown(
            label='Response Style',
            choices=STYLES,
            allow_custom_value=True,
        )

    with gr.Row():
        message_input = gr.Textbox(
            placeholder='Message',
            lines=3,
            show_label=False,
            container=False,
            scale=1,
        )
        send_button = gr.Button('Send', variant='primary', scale=0)
        stop_button = gr.Button('Stop', variant='stop', visible=False, scale=0)

    # Controller

    @on(demo.load)
    def default_to_latest(session: session_state) -> {model_input, context_input}:
        return {
            model_input: gr.update(
                value=session.models[-1],
                choices=session.models,
            ),
            context_input: gr.update(
                value=session.contexts[-1],
                choices=session.contexts,
            ),
        }

    @on(model_input.change)
    def change_model(session: session_state, model: model_input) -> model_input:
        return gr.update(
            value=session.set_model(model),
            choices=session.models,
        )

    @on(context_input.change)
    def change_context(
        session: session_state,
        context: context_input
    ) -> {
        context_input,
        motive_input,
    }:
        return {
            context_input: gr.update(
                value=session.set_context(context),
                choices=session.contexts,
            ),
            motive_input: session.context.motive,
        }

    @on(send_button.click)
    def get_chat_response(
        session: session_state,
        motive: motive_input,
        style: style_input,
        message: message_input,
        chat: chat_log
    ) -> {
        message_input,
        chat_log,
        send_button,
        stop_button,
    }:
        log = ''
        response = ''
        preview = [message, None]
        chat.append(preview)
        progress = {
            message_input: locked(),
            chat_log: chat,
            send_button: hide(),
            stop_button: show(),
        }
        yield progress

        for change in session.get_response(message, motive, style):
            response = change.get('response', '')
            status = change.get('status', '')
            log = change.get('log', '')

            preview[1] = response
            if status: preview[1] += note(status)
            if log: preview[1] += fold(log)
            yield progress

        preview[1] = response
        if log: preview[1] += fold(log)
        if not status: message = ''
        progress[message_input] = unlocked(value=message)
        progress[send_button] = show()
        progress[stop_button] = hide()
        yield progress

    @on(stop_button.click, cancels=[get_chat_response])
    def stop_chat_response() -> {message_input, send_button, stop_button}:
        return {
            message_input: unlocked(),
            send_button: show(),
            stop_button: hide(),
        }
