import gradio as gr

from contexts import CONTEXTS
from oracle.session import ChatSession
from oracle.gradio.config import STYLES
from oracle.gradio.utils import *


with gr.Blocks(title='Oracle', css='oracle/gradio/gui.css').queue() as demo:
    # Model

    session_state = gr.State(ChatSession)

    # View

    chatbot_history = gr.Chatbot(elem_id='chatbot', show_label=False)

    with gr.Accordion('Settings', open=False, elem_id='settings'):
        with gr.Row():
            model_input = gr.Dropdown(
                label='Chat Model',
                allow_custom_value=True,
                scale=1,
            )
            model_reload = gr.Button('Reload', scale=0)

        with gr.Row():
            context_input = gr.Dropdown(
                label='Source',
                allow_custom_value=False,
            )
            context_reload = gr.Button('Reload', scale=0)

        motive_input = gr.Dropdown(
            label='Motivation',
            allow_custom_value=True,
        )
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

    demo.load(
        guard(lambda session: gr.update(choices=session.models)),
        inputs=[session_state],
        outputs=model_input,
    )
    demo.load(
        guard(lambda session: gr.update(choices=session.contexts)),
        inputs=[session_state],
        outputs=context_input,
    )
    demo.load(
        guard(lambda session: session.models[-1]),
        inputs=[session_state],
        outputs=model_input,
    )
    demo.load(
        guard(lambda session: session.contexts[-1]),
        inputs=[session_state],
        outputs=context_input,
    )

    model_input.change(
        guard(lambda session, model: gr.update(
            value=session.set_model(model),
            choices=session.models,
        )),
        inputs=[session_state, model_input],
        outputs=model_input,
    )

    context_input.change(
        guard(lambda session, context: gr.update(
            value=session.set_context(context),
            choices=session.contexts,
        )),
        inputs=[session_state, context_input],
        outputs=context_input,
    )
    context_input.change(
        guard(lambda session: gr.update(
            value=session.context.motive,
            choices=[session.context.motive],
        )),
        inputs=session_state,
        outputs=motive_input,
    )

    model_reload.click(
        guard(lambda session: gr.update(choices=session.reload_models())),
        inputs=session_state,
        outputs=model_input,
    )
    context_reload.click(
        guard(lambda session: gr.update(choices=session.reload_contexts())),
        inputs=session_state,
        outputs=context_input,
    )

    def chat_handler(chat, motive, style, message, chatbot):
        log = ''
        response = ''
        preview = [message, None]
        chatbot.append(preview)
        progress = {
            message_input: locked(),
            chatbot_history: chatbot,
            send_button: hide(),
            stop_button: show(),
        }
        yield progress

        for change in chat(message, motive, style):
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

    chat_thread = send_button.click(
        chat_handler,
        inputs=[session_state, motive_input, style_input, message_input, chatbot_history],
        outputs={message_input, chatbot_history, send_button, stop_button},
    )

    stop_button.click(
        lambda: {
            message_input: unlocked(),
            send_button: show(),
            stop_button: hide(),
        },
        outputs={message_input, send_button, stop_button},
        cancels=[chat_thread],
    )
