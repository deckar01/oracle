from pkgutil import iter_modules
from importlib import import_module

from oracle.log import log_error


class none:
    name = 'None'
    motive = "Your are an AI chat bot. Reply to the following message."
    def find(self, _):
        return ()

CONTEXTS = {'None': none}

for _, module_name, _ in iter_modules(['contexts']):
    try:
        module = import_module(f'contexts.{module_name}')
        if not hasattr(module, 'Context'):
            continue
        CONTEXTS[module.Context.name] = module.Context
    except:
        log_error()
