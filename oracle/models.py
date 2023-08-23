from threading import Thread
from typing import Iterable

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, TextIteratorStreamer


if torch.cuda.is_available() and torch.cuda.device_count():
    DEVICE = 'cuda'
else:
    DEVICE = 'cpu'


class ChatModel:
    max_tokens: int
    tokenizer: AutoTokenizer
    model: AutoModelForCausalLM
    min_reply_tokens: int = 256
    device: str = DEVICE

    context = None
    inputs = None
    length = None
    log = ''

    system_prompt = ''
    context_prompt = ''
    user_prompt = ''
    format_prompt = ''
    response_prompt =  '### Response:\n'

    def prepare(self):
        if self.context:
            context = '\n'.join(self.context)
            self.context_prompt = f'### Search results:\n{context}\n\n'

        self.prompt = self.log = ''.join((
            self.system_prompt,
            self.context_prompt,
            self.user_prompt,
            self.format_prompt,
            self.response_prompt,
        ))
        self.inputs = self.tokenizer(
            self.prompt,
            return_tensors='pt',
            return_length=True,
            verbose=False,
        ).to(self.device)

        self.length = self.inputs.length[0]
        del self.inputs['length']

        # Handle token overflow by discardling less relevant context.
        if self.length > self.max_tokens - self.min_reply_tokens:
            if self.context:
                self.context = self.context[:-1]
                return self.prepare()
            else:
                raise ValueError('The message is too long.')
    
    def _reply(self, stream):
        self.model.generate(
            **self.inputs,
            streamer=stream,
            do_sample=True,
            top_p=0.95,
            top_k=0, 
            max_new_tokens=self.max_tokens - self.length,
        )

    def reply(self, message: str) -> Iterable[str]:
        self.user_prompt = f'### Message:\n{message}\n\n'
        self.prepare()
        stream = TextIteratorStreamer(
            self.tokenizer,
            skip_prompt=True,
            skip_special_tokens=True,
        )
        thread = Thread(target=self._reply, args=(stream,))
        thread.start()
        for chunk in stream:
            self.log += chunk
            yield self.log[len(self.prompt):]

    def coach(self, motive: str):
        if motive:
            self.system_prompt = f'### System:\n{motive}\n\n'

    def study(self, context: list[str]):
        # TODO: Stream context and token lengths.
        self.context = list(context)

    def mask(self, style: str):
        if style:
            self.format_prompt = f'### Response format:\n{style}\n\n'


class StableBeluga7B(ChatModel):
    max_tokens = 4096
    tokenizer = AutoTokenizer.from_pretrained('models/StableBeluga-7B')
    model = AutoModelForCausalLM.from_pretrained(
        'models/StableBeluga-7B',
        torch_dtype=torch.float16 if DEVICE == 'cuda' else None,
        low_cpu_mem_usage=True,
        device_map='auto',
        offload_folder="models/StableBeluga-7B/offload",
    )
