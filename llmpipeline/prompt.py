import json

class Prompt:
    def __init__(self, text, keys):
        self.text = text
        self.keys = keys
    
    def __call__(self, *inps):
        t = self.text
        for a, b in zip(self.keys, inps):
            if b is None: b = str(b)
            elif type(b) is not str: b = json.dumps(b, ensure_ascii=False)
            t = t.replace(a, b)
        return t
