"""
A web client built using the Blocks API from the Gradio framework.
The UI is designed with nested components, event handlers. Chat
requests are queued one at a time. Sessions are persisted in an
SQLite database. Updates are streamed over websockets. Chat
operations are streamed from the Flask API and form options are
read from its OpenAPI schema.
"""

import gradio as gr

from .api import Oracle
from .event import on, after, note, fold, show, hide, locked, unlocked
from .session import persist
from .theme import theme, css


with gr.Blocks(title='Oracle', theme=theme, css=css) as demo:
    # Model

    oracle_state = gr.State(Oracle)
    raw_chat_log = persist("chat", gr.State(list))

    # View

    gr.Tab('Oracle', elem_id='nomenu')

    with gr.Tab('Context'):
        context_input = persist("context", gr.Dropdown(label='Source'))
        motive_input = persist("motive", gr.Textbox(label='Motivation', lines=1))
        use_keywords_checkbox = persist("use_keywords", gr.Checkbox(
            True,
            label='Ask the model for keywords?',
        ))
        debug_checkbox = persist("debug", gr.Checkbox(label='Show debug info?'))

    with gr.Tab('Model'):
        model_input = persist("model", gr.Dropdown( label='Chat Model'))
        style_input = persist("style", gr.Dropdown(
            label='Response Style',
            allow_custom_value=True,
        ))

    with gr.Tab('Session'):
        with gr.Accordion('Advanced', open=False):
            clear_session_button = gr.Button('Clear Session', variant='stop')

    chat_log = gr.Chatbot(elem_id='chatbot', show_label=False)

    with gr.Row():
        message_input = gr.Textbox(
            placeholder='Send a message',
            lines=3,
            min_width=600,
            show_label=False,
            container=False,
            scale=99,
        )
        send_button = gr.Button('Send', variant='primary', scale=1)
        stop_button = gr.Button('Stop', variant='stop', visible=False, scale=1)

    # Controller

    demo.queue(api_open=False, concurrency_count=8)

    @after(context_input.resume)
    def default_contexts(oracle: oracle_state, context: context_input) -> context_input:
        return gr.update(**oracle.defaults('context', context))

    @after(model_input.resume)
    def default_models(oracle: oracle_state, model: model_input) -> model_input:
        return gr.update(**oracle.defaults('model', model))

    @after(style_input.resume)
    def default_styles(oracle: oracle_state, style: style_input) -> style_input:
        return gr.update(**oracle.defaults('style', style))

    @on(context_input.change)
    def default_motive(oracle: oracle_state, context: context_input) -> motive_input:
        return oracle.default_for('motive', context)

    @on(context_input.change)
    def change_placeholder(context: context_input) -> message_input:
        placeholder = 'Send a message'
        if context and context != 'None':
            placeholder += f' about {context}'
        return gr.update(placeholder=placeholder)

    def refresh_chat(raw_chat: raw_chat_log, debug: debug_checkbox) -> chat_log:
        preview = []
        for exchange in raw_chat:
            message = exchange.get('message', '')
            response = exchange.get('response', '')
            status = exchange.get('status', None)
            if status and status != 'done':
                response += note(status)
            if debug:
                response += fold('Debug', exchange.get('logs', {}))
            preview.append((message, response or None))
        return preview

    after(raw_chat_log.resume, refresh_chat)
    on(debug_checkbox.change, refresh_chat)

    @on(send_button.click, queue=True)
    def get_chat_response(
        message: message_input,
        context: context_input,
        model: model_input,
        motive: motive_input,
        style: style_input,
        use_keywords: use_keywords_checkbox,
        debug: debug_checkbox,
        raw_chat: raw_chat_log,
        chat: chat_log,
        request: gr.Request,
        oracle: oracle_state,
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

        stream = oracle.stream(
            message=message,
            context=context,
            model=model,
            motive=motive,
            style=style,
            use_keywords=use_keywords,
        )
        for event in stream:
            preview.update(event)
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
