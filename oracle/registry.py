import importlib

import oracle.log


class Registry:
    def __init__(self, module):
        self.module = module
        self.load()
        self.cache = {}
        self.instance = None

    def load(self, reload=False):
        if reload:
            importlib.reload(self.module)
        self.map = self.module.MAP

    @property
    def names(self): return list(self.map.keys())

    def use(self, name):
        try:
            name = name or 'None'
            if name not in self.cache:
                self.cache[name] = self.map[name]()
            return self.cache[name]

        except Exception:
            oracle.log.error()
            self.map.pop(name, None)
