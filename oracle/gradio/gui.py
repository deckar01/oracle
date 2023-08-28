import gradio as gr

from oracle.session import ChatSession
from .config import STYLES
from .utils import *


with gr.Blocks(title='Oracle', css='oracle/gradio/gui.css').queue() as demo:
    # Model

    session_state = gr.State(ChatSession)
    raw_chat_log = persist(gr.State(list))

    # View

    with gr.Accordion('☰', open=False, elem_id='settings'):
        with gr.Tab('Context'):
            context_input = persist(gr.Dropdown(label='Source'))
            motive_input = persist(gr.Textbox(label='Motivation'))
            keyword_checkbox = persist(gr.Checkbox(True, label='Ask the model for keywords?'))
            debug_checkbox = persist(gr.Checkbox(label='Show debug info?'))

        with gr.Tab('Model'):
            model_input = persist(gr.Dropdown(label='Chat Model'))
            style_input = persist(gr.Dropdown(
                label='Response Style',
                choices=STYLES,
                allow_custom_value=True,
            ))

        with gr.Tab('Session'):
            clear_session_button = gr.Button('Clear Session', variant='stop')

    chat_log = gr.Chatbot(elem_id='chatbot', show_label=False)

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
    def load_defaults(
        raw_chat: raw_chat_log,
        debug: debug_checkbox,
        session: session_state,
    ) -> {
        chat_log,
        model_input,
        context_input,
    }:
        return {
            chat_log: refresh_chat(raw_chat, debug),
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

    def refresh_chat(
        raw_chat: raw_chat_log,
        debug: debug_checkbox,
    ) -> chat_log:
        preview = []
        for exchange in raw_chat:
            message = exchange.get('message', '')
            response = exchange.get('response', '')
            status = exchange.get('status', None)
            if status and status != 'done':
                response += note(status)
            if debug:
                for name, log in exchange.get('logs', {}).items():
                    response += fold(log, name)
            preview.append((message, response or None))
        return preview

    on(debug_checkbox.change, refresh_chat)

    @on(send_button.click)
    def get_chat_response(
        session: session_state,
        keyword: keyword_checkbox,
        motive: motive_input,
        style: style_input,
        debug: debug_checkbox,
        message: message_input,
        raw_chat: raw_chat_log,
        chat: chat_log,
        request: gr.Request,
    ) -> {
        message_input,
        raw_chat_log,
        chat_log,
        send_button,
        stop_button,
    }:
        preview = {}
        raw_chat.append(preview)
        progress = {
            message_input: locked(),
            raw_chat_log: raw_chat,
            chat_log: chat,
            send_button: hide(),
            stop_button: show(),
        }
        yield progress

        for change in session.get_response(message, motive, style, keyword):
            preview.update(change)
            progress[chat_log] = refresh_chat(raw_chat, debug)
            yield progress

        raw_chat_log.change(raw_chat, request)

        if preview.get('status', None) == 'done':
            message = ''
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

    @on(clear_session_button.click)
    def clear_session(request: gr.Request) -> {raw_chat_log, chat_log}:
        raw_chat_log.change([], request)
        return {
            raw_chat_log: [],
            chat_log: refresh_chat([], False)
        }
