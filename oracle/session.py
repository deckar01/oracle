import importlib

import oracle
import oracle.contexts
import oracle.models


MODEL_CACHE = {}
CONTEXT_CACHE = {}


class ChatSession:
    def __init__(self):
        self.reload_models()
        self.MODELS = oracle.models.MODELS
        self.models = list(self.MODELS.keys())

        self.reload_contexts()
        self.CONTEXTS = oracle.contexts.CONTEXTS
        self.contexts = list(self.CONTEXTS.keys())

        self.set_model(self.models[0])
        self.set_context(self.contexts[0])

    def reload_models(self):
        importlib.reload(oracle.models)
        self.MODELS = oracle.models.MODELS
        self.models = list(self.MODELS.keys())
        return self.models

    def reload_contexts(self):
        importlib.reload(oracle.contexts)
        self.CONTEXTS = oracle.contexts.CONTEXTS
        self.contexts = list(self.CONTEXTS.keys())
        return self.contexts

    def set_model(self, model, reload=False):
        try:
            # https://github.com/gradio-app/gradio/issues/5348
            if model not in self.MODELS:
                return self.model.name
            
            if reload:
                MODEL_CACHE.clear()
                self.reload_models()

            if model not in MODEL_CACHE:
                self.model = None
                if model != 'None':
                    # Keep the model cached while not in use
                    MODEL_CACHE.clear()
                MODEL_CACHE[model] = self.MODELS[model]()
            self.model = MODEL_CACHE[model]

        except:
            oracle.log_error()
            self.MODELS.pop(model, None)

        return self.model.name

    def set_context(self, context, reload=False):
        try:
            # https://github.com/gradio-app/gradio/issues/5348
            if context not in self.CONTEXTS:
                return self.context.name

            if reload:
                CONTEXT_CACHE.clear()
                self.reload_contexts()

            if context not in CONTEXT_CACHE:
                self.context = None
                if context != 'None':
                    # Keep the context cached while not in use
                    CONTEXT_CACHE.clear()
                CONTEXT_CACHE[context] = self.CONTEXTS[context]()
            self.context = CONTEXT_CACHE[context]

        except:
            oracle.log_error()
            if context in self.CONTEXTS:
                self.CONTEXTS.pop(context, None)

        return self.context.name

    def get_response(self, message, motive=None, style=None, use_keywords=False):
        try:
            logs = {}
            progress = dict(message=message)
            yield progress

            if use_keywords and self.context.name != 'None':
                progress.update(status='reading...')
                yield progress
                keyword_motive = 'Produce a list of keywords related to the following message that can be used to search for a response.'
                keyword_style = 'A comma separated list of 8 to 24 keywords.'
                keywords = ''.join(self.model.reply(message, motive=keyword_motive, style=keyword_style))
                logs['Keyword Log'] = getattr(self.model, 'log', None)
            else:
                keywords = message

            progress = dict(status='researching...')
            yield progress
            context = self.context.find(keywords)

            progress.update(status='thinking...')
            yield progress
            options = dict(motive=motive, style=style, context=context)
            progress.update(response='')
            for chunk in self.model.reply(message, **options):
                progress['response'] += chunk
                yield progress

            progress.update(status='done')
            logs['Response Log'] = getattr(self.model, 'log', None)
            progress.update(logs=logs)
            yield progress

            for log in progress['logs'].values(): oracle.log(log)

        except GeneratorExit:
            raise
        except:
            error = oracle.log_error()
            yield dict(status='error', response='Error', logs={'Debug': error})
