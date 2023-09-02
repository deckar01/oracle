"""
The core logic for streaming chat responses.
Models and contexts are dynamically loaded from module registries,
lazy loaded, and cached in memory between chat sessions.
"""

import json

import oracle.log
import oracle.contexts
import oracle.models
import oracle.styles
from .registry import Registry


Model = Registry(oracle.models)
Context = Registry(oracle.contexts)
Style = Registry(oracle.styles)

def chat(
    message,
    context,
    model,
    motive,
    style,
    use_keywords,
):
    try:
        progress = dict(message=message, response='', status='loading...', logs={})
        yield progress

        context = Context.use(context)
        model = Model.use(model)

        if use_keywords and context.name != 'None':
            progress.update(status='reading...')
            yield progress
            keyword_motive = 'Produce a list of keywords related to the following '\
                'message that can be used to search for a response.'
            keyword_style = 'A comma separated list of 8 to 24 keywords.'
            response = model.reply(message, motive=keyword_motive, style=keyword_style)
            keywords = ''
            for chunk in response:
                keywords += chunk
            progress['logs']['Keyword Generation'] = getattr(model, 'log', None)
        else:
            keywords = message

        progress.update(status='researching...')
        yield progress
        docs = list(context.find(keywords))
        if docs:
            progress['logs']['Search Results'] = {
                doc.split('\n', 1)[0]: doc
                for doc in docs
            }

        progress.update(status='thinking...')
        yield progress
        options = dict(
            motive=motive or context.motive,
            style=style if style != 'None' else None,
            context=docs,
        )
        for chunk in model.reply(message, **options):
            if chunk:
                progress['response'] += chunk
                yield progress

        progress.update(status='done')
        if log := getattr(model, 'log', None):
            progress['logs']['Full Prompt'] = log

        yield progress

    except Exception:
        oracle.log.error()
        progress.update(status='error')
    finally:
        yield progress
        if logs := progress['logs']:
            oracle.log.write(json.dumps(logs))
