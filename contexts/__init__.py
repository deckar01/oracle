from pkgutil import iter_modules
from importlib import import_module


class none:
    name = 'None'
    motive = "Your are an AI chat bot. Answer the following question."
    find = None

CONTEXTS = {'None': none}
CONTEXTS.update(
    (context.name, context)
    for _, module_name, _ in iter_modules(['contexts'])
    if (context := import_module(f'contexts.{module_name}'))
    if hasattr(context, 'name')
)
