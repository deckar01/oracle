import traceback

from contexts import CONTEXTS
from oracle.log import log
from oracle.models import StableBeluga7B


def chat(message, motive=None, source=None, style=None):
    try:
        # TODO: Select other models.
        model = StableBeluga7B()
        model.coach(motive)
        model.mask(style)

        context = CONTEXTS[source]
        if context.find:
            yield dict(status='searching...')
            model.study(context.find(message))

        yield dict(status='thinking...')

        for progress in model.reply(message):
            yield dict(response=progress, status='...')

        yield dict(response=progress, log=model.log)
        log('history', model.log)

    except:
        error = traceback.format_exc()
        yield dict(status='Error', response='Error', log=error)
        log('history/errors', error)
