import importlib

import oracle.models
from oracle.log import log, log_error
import contexts


MODEL_CACHE = {}
CONTEXT_CACHE = {}


class ChatSession:
    def __init__(self):
        self.reload_models()
        self.MODELS = oracle.models.MODELS
        self.models = list(self.MODELS.keys())

        self.reload_contexts()
        self.CONTEXTS = contexts.CONTEXTS
        self.contexts = list(self.CONTEXTS.keys())

        self.set_model(self.models[0])
        self.set_context(self.contexts[0])

    def reload_models(self):
        importlib.reload(oracle.models)
        self.MODELS = oracle.models.MODELS
        self.models = list(self.MODELS.keys())
        return self.models

    def reload_contexts(self):
        importlib.reload(contexts)
        self.CONTEXTS = contexts.CONTEXTS
        self.contexts = list(self.CONTEXTS.keys())
        return self.contexts

    def set_model(self, model):
        try:
            # https://github.com/gradio-app/gradio/issues/5348
            if model not in self.MODELS:
                return self.model_name

            if model not in MODEL_CACHE:
                self.model = None
                if model != 'None':
                    # Keep the model cached while not in use
                    MODEL_CACHE.clear()
                MODEL_CACHE[model] = self.MODELS[model]()
            self.model = MODEL_CACHE[model]
            self.model_name = model

        except:
            log_error()
            self.MODELS.pop(model, None)

        return self.model_name

    def set_context(self, context):
        try:
            # https://github.com/gradio-app/gradio/issues/5348
            if context not in self.CONTEXTS:
                return self.model_name

            if context not in CONTEXT_CACHE:
                self.context = None
                if context != 'None':
                    # Keep the context cached while not in use
                    CONTEXT_CACHE.clear()
                CONTEXT_CACHE[context] = self.CONTEXTS[context]()
            self.context = CONTEXT_CACHE[context]
            self.context_name = context

        except:
            log_error()
            if context in self.CONTEXTS:
                self.CONTEXTS.pop(context, None)

        return self.context_name

    def __call__(self, message, motive=None, style=None):
        try:
            yield dict(status='searching...')
            context = self.context.find(message)

            yield dict(status='thinking...')
            options = dict(motive=motive, style=style, context=context)
            for progress in self.model.reply(message, **options):
                yield dict(response=progress, status='...', log=self.model.log)

            yield dict(response=progress, log=self.model.log)
            log(self.model.log)
        except GeneratorExit:
            raise
        except:
            error = log_error()
            yield dict(status='Error', response='Error', log=error)
