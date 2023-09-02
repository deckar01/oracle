"""
A registry of text generation AI models (LLMs).
"""

from pkgutil import iter_modules
from importlib import import_module, reload

import oracle.log


class NoModel:
    name = 'None'

    def reply(self, message, *, context, **_):
        if context:
            return ['\n\n'.join(f'```\n{c}\n```' for c in context)]
        else:
            return [message]


MAP = {'None': NoModel}

for _, module_name, _ in iter_modules(['oracle/models']):
    try:
        module = import_module(f'oracle.models.{module_name}')
        module = reload(module)
        if not hasattr(module, 'Model'):
            continue
        MAP[module.Model.name] = module.Model
    except Exception:
        oracle.log.error()
