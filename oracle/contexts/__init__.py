"""
A registry of sources of context used to improve
responses with domain specific information.
"""

from pkgutil import iter_modules
from importlib import import_module, reload

import oracle.log


class none:
    name = 'None'
    motive = "Your are an AI chat bot. Reply to the following message."
    def find(self, _):
        return ()

MAP = {'None': none}

for _, module_name, _ in iter_modules(['oracle/contexts']):
    try:
        module = import_module(f'oracle.contexts.{module_name}')
        module = reload(module)
        if not hasattr(module, 'Context'):
            continue
        MAP[module.Context.name] = module.Context
    except Exception:
        oracle.log.error()
