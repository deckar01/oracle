from pkgutil import iter_modules
from importlib import import_module, reload
from threading import Thread, Event

import oracle


class ThreadStopper:
    def __init__(self):
        self.event = Event()

    def __call__(self, *args, **kwargs):
        return self.event.is_set()

    def stop(self):
        return self.event.set()


class TransformersModel:
    name: str
    model_id: str
    max_tokens: int

    min_reply_tokens: int = 256
    response_prompt =  '### Response:\n'

    log = None

    def __init__(self):
        from transformers import AutoModelForCausalLM, AutoTokenizer
        import torch

        self.device = oracle.get_device()
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_id)
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_id,
            torch_dtype=torch.float16 if self.device == 'cuda' else None,
            low_cpu_mem_usage=True,
            device_map='auto',
            offload_folder=".offload",
        )

    def get_inputs(self, message, motive, style, context):
        prompt = ''

        if motive:
            prompt += f'### System:\n{motive}\n\n'

        if context:
            context = list(context)
            context_string = '\n'.join(context)
            prompt += f'### Search results:\n{context_string}\n\n'

        prompt += f'### Message:\n{message}\n\n'

        if style:
            prompt += f'### Response format:\n{style}\n\n'

        prompt += self.response_prompt
        self.log = f'[model: {self.name}]\n\n{prompt}'

        tokenizer_options = dict(return_tensors='pt', return_length=True, verbose=False)
        inputs = self.tokenizer(prompt, **tokenizer_options).to(self.device)

        length = inputs.length[0]
        del inputs['length']

        # Handle token overflow by discardling less relevant context.
        if length > self.max_tokens - self.min_reply_tokens:
            if context:
                # TODO: Stream context and token lengths.
                return self.get_inputs(message, motive, style, context[:-1])
            else:
                raise ValueError('The message is too long.')
    
        inputs.update(max_new_tokens=self.max_tokens - length)
        return inputs

    def reply(
        self,
        message: str,
        *,
        motive: str = None,
        style: str = None,
        context: list[str] = None,
    ):
        from transformers import TextIteratorStreamer, StoppingCriteriaList

        # Tokenize the prompt
        generate_options = self.get_inputs(message, motive, style, context)

        # Configure the model to stream output
        stream_options = dict(skip_prompt=True, skip_special_tokens=True)
        stream = TextIteratorStreamer(self.tokenizer, **stream_options)
        generate_options.update(streamer=stream)

        # Allow stopping the generate thread early
        stopper = ThreadStopper()
        stoppers = StoppingCriteriaList([stopper])
        generate_options.update(stopping_criteria=stoppers)

        # Configure the sampling strategy
        generate_options.update(do_sample=True)
        generate_options.update(top_p=0.95)
        generate_options.update(top_k=0)

        # Run the model in a thread for streaming
        thread = Thread(
            target=self.model.generate,
            kwargs=generate_options,
            daemon=True,
        )
        thread.start()

        try:
            # Stream the response
            for chunk in stream:
                yield chunk
                self.log += chunk
        finally:
            # Stop the thread with an event
            stopper.stop()
            thread.join()


class NoModel:
    name = 'None'

    def reply(self, message, *, context, **_):
        if context:
            return ['\n\n'.join(f'```\n{c}\n```' for c in context)]
        else:
            return [message]


MODELS = {'None': NoModel}

for _, module_name, _ in iter_modules(['oracle/models']):
    try:
        module = import_module(f'oracle.models.{module_name}')
        module = reload(module)
        if not hasattr(module, 'Model'):
            continue
        MODELS[module.Model.name] = module.Model
    except:
        oracle.log_error()
