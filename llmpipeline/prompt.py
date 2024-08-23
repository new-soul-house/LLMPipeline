import json
import importlib
from pathlib import Path
from .log import log

class PromptKeys:
    def __init__(self, arr, prompt):
        self._arr = arr.copy()
        self.prompt = prompt

    def __getitem__(self, index):
        return self._arr[index]

    def __setitem__(self, index, value):
        log.debug(f'Change prompt "{self.prompt.name}" keys [{index}] to: {value}')
        self._arr[index] = value
        self.prompt.save()

    def __str__(self):
        return str(self._arr)

class Prompt:
    def __init__(self, text, keys, name, file=None):
        self.name = name
        self.file = file
        self.__text = text
        self.__keys = PromptKeys(keys, self)

    @property
    def text(self):
        return self.__text

    @text.setter
    def text(self, value):
        log.debug(f'Change prompt "{self.name}" text to: {value}')
        self.__text = value
        self.save()

    @property
    def keys(self):
        return self.__keys

    @keys.setter
    def keys(self, value):
        log.debug(f'Change prompt "{self.name}" keys to: {value}')
        self.__keys = value
        self.save()

    def __call__(self, *inps):
        t = self.__text
        for a, b in zip(self.__keys, inps):
            if b is None: b = str(b)
            elif type(b) is not str: b = json.dumps(b, ensure_ascii=False)
            t = t.replace(a, b)
        return t

    def save(self):
        if self.file is not None:
            log.debug(f'Save prompt [{self.name}] to: {self.file}')
            with open(self.file, 'w') as f:
                f.write(f'prompt="""{self.text}"""\nkeys={self.keys}')


class PromptManager:
    def __init__(self, prompts_dir):
        log.debug('Setup PromptManager')
        self.prompts_dir = Path(prompts_dir)
        self.prompts = {}
        self.load_prompts()

    def load_prompts(self):
        self.prompts = {}
        log.debug(f'Start load prompts: {self.prompts_dir}')
        prompt_files = list(self.prompts_dir.glob('*_prompt.py'))
        log.debug(f'Find {len(prompt_files)} prompt files: {[p.stem for p in prompt_files]}')

        for pf in prompt_files:
            m = importlib.import_module(f'{str(self.prompts_dir).replace("/",".")}.{pf.stem}')
            self.prompts[pf.stem] = Prompt(m.prompt, m.keys, pf.stem, pf)

        log.debug('All prompts loaded')
