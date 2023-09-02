import json
import requests


class Oracle:
    API = 'http://localhost:8081'

    def __init__(self):
        try:
            self.spec = requests.get(f'{self.API}/spec').json()
            params = self.spec['paths']['/chat']['post']['parameters']
            self.params = {param['name']: param for param in params}
        except Exception:
            self.spec = None
            self.params = {}

    def stream(self, **params):
        with requests.Session() as session:
            stream = session.post(f'{self.API}/chat', stream=True, params=params)
            for line in stream.iter_lines():
                yield json.loads(line)

    def defaults(self, name, value=None):
        if not self.spec:
            return {}
        schema = self.params[name]['schema']
        meta = {}
        if default := schema.get('default', None):
            meta['value'] = value or default
        if choices := schema.get('enum', None):
            meta['choices'] = choices
        elif examples := schema.get('x-examples', None):
            meta['choices'] = examples
        return meta

    def default_for(self, name, control):
        if not self.spec:
            return None
        schema = self.params[name]['schema']
        return schema.get('x-defaults', {}).get(control, None)
