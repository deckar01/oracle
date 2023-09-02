"""
The base model for all HuggingFace models. This handles building
prompt strings and running the model in a separate thread to stream
the response as it is being generated.
"""

from threading import Thread

import oracle.device


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

        self.device = oracle.device.get()
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
        inputs.update(max_new_tokens=self.max_tokens - length)
        del inputs['length']
        return inputs

    def reply(
        self,
        message: str,
        *,
        motive: str = None,
        style: str = None,
        context: list[str] = None,
    ):
        from transformers import TextIteratorStreamer

        # Tokenize the prompt
        while True:
            generate_options = self.get_inputs(message, motive, style, context)
            max_new_tokens = generate_options['max_new_tokens']
            if context and max_new_tokens < self.min_reply_tokens:
                context = context[:-1]
            else:
                break

        # Configure the model to stream output
        stream_options = dict(skip_prompt=True, skip_special_tokens=True)
        stream = TextIteratorStreamer(self.tokenizer, **stream_options)
        generate_options.update(streamer=stream)

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
            thread.join()

