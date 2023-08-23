from threading import Thread

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, TextIteratorStreamer


class ChatModel:
    max_tokens: int
    tokenizer: AutoTokenizer
    model: AutoModelForCausalLM
    min_reply_tokens: int = 256
    device: str = 'cuda'

    inputs = None
    length = None
    log = ''

    system_prompt = ''
    context_prompt = ''
    question_prompt = ''
    format_prompt = ''
    answer_prompt =  '### Answer:\n'

    def prepare(self):
        self.prompt = ''.join((
            self.system_prompt,
            self.context_prompt,
            self.question_prompt,
            self.format_prompt,
            self.answer_prompt,
        ))
        self.log = self.prompt
        self.inputs = self.tokenizer(
            self.prompt,
            return_tensors='pt',
            return_length=True,
            verbose=False,
        ).to(self.device)
        self.length = self.inputs.length[0]
        del self.inputs['length']
    
    def _reply(self, streamer):
        self.model.generate(
            **self.inputs,
            streamer=streamer,
            do_sample=True,
            top_p=0.95,
            top_k=0, 
            max_new_tokens=self.max_tokens - self.length,
        )

    def reply(self):
        decode_kwargs = dict(skip_special_tokens=True)
        streamer = TextIteratorStreamer(
            self.tokenizer,
            skip_prompt=True,
            decode_kwargs=decode_kwargs
        )
        thread = Thread(target=self._reply, args=(streamer,))
        thread.start()
        for chunk in streamer:
            self.log += chunk
            yield self.log[len(self.prompt):]

    def coach(self, motivation):
        if motivation:
            self.system_prompt = f'### System:\n{motivation}\n\n'

    def ask(self, question):
        self.question_prompt = f'### Question:\n{question}\n\n'

    def set_format(self, style):
        if style:
            self.format_prompt = f'### Answer format:\n{style}\n\n'

    def set_context(self, context):
        sources = '\n'.join(context)
        self.context_prompt = f'### Search results:\n{sources}\n\n'

    @property
    def overflow(self):
        return self.length > self.max_tokens - self.min_reply_tokens


class StableBeluga7B(ChatModel):
    max_tokens = 4096
    tokenizer = AutoTokenizer.from_pretrained('models/StableBeluga-7B')
    model = AutoModelForCausalLM.from_pretrained(
        'models/StableBeluga-7B',
        torch_dtype=torch.float16,
        low_cpu_mem_usage=True,
        device_map='cuda:0',
    )
