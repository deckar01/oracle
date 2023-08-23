import traceback

from contexts import CONTEXTS
from oracle.log import log
from oracle.models import StableBeluga7B


def chat(question, format=None, source=None, motivation=None):
    try:
        # TODO: Select other models.
        model = StableBeluga7B()
        context = CONTEXTS[source]
        model.coach(motivation)
        model.ask(question)
        model.set_format(format)

        if context.find:
            yield dict(status='searching...')
            references = list(context.find(question))
            model.set_context(references)

        yield dict(status='thinking...')
        model.prepare()

        if context.find:
            # TODO: Stream find() and optimize with partial token lengths.
            while model.overflow and references:
                references.pop()
                model.set_context(references)
                model.prepare()

        if model.overflow:
            raise ValueError('The question is too long.')

        for progress in model.reply():
            yield dict(response=progress, status='...')

        yield dict(response=progress, log=model.log)
        log('history', model.log)

    except:
        message = traceback.format_exc()
        yield dict(status='Error', response='Error', log=message)
        log('history/errors', message)
