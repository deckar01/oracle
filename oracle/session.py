from contexts import CONTEXTS
from oracle.log import log, log_error
from oracle.models import MODELS


MODEL_CACHE = {}
CONTEXT_CACHE = {}


class ChatSession:
    def __init__(self):
        self.models = list(MODELS.keys())
        self.contexts = list(CONTEXTS.keys())
        self.set_model(self.models[0])
        self.set_context(self.contexts[0])

    def set_model(self, model):
        try:
            # TODO: Purge / timeout old models?
            if model not in MODEL_CACHE:
                MODEL_CACHE[model] = MODELS[model]()
            self.model = MODEL_CACHE[model]
            self.model_name = model
            return model

        except:
            log_error()
            del MODELS[model]
            return self.model_name

    def set_context(self, context):
        try:
            # TODO: Purge / timeout old context?
            if context not in CONTEXT_CACHE:
                CONTEXT_CACHE[context] = CONTEXTS[context]()
            self.context = CONTEXT_CACHE[context]
            self.context_name = context
            return context

        except:
            log_error()
            del CONTEXTS[context]
            return self.context_name

    def __call__(self, message, motive=None, style=None):
        try:
            yield dict(status='searching...')
            context = self.context.find(message)

            yield dict(status='thinking...')
            options = dict(motive=motive, style=style, context=context)
            for progress in self.model.reply(message, **options):
                yield dict(response=progress, status='...')

            yield dict(response=progress, log=self.model.log)
            log(self.model.log)

        except:
            error = log_error()
            yield dict(status='Error', response='Error', log=error)
