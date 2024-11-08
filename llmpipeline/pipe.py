import re
import time
import json
from .log import log

class LLMPipe:
    def __init__(self, name, prompt=None, return_json=True, format=None, llm=None, verbose=True, retry=5, inp=None, out=None, lock=None, run_time=None, inout_log=None, **kargs):
        self.name = name
        self.prompt = prompt
        self.llm = llm
        self.return_json = return_json
        self.format = format
        self.verbose = verbose
        self.retry = retry
        self.log = lambda n, t: log.debug(f'[{name}] {n}: {t}') if self.verbose else None

        # multiprocess lock
        self.lock = lock
        self.run_time = run_time if run_time is not None else []
        self.inout_log = inout_log if inout_log is not None else []

    @property
    def time(self):
        if self.run_time:
            return sum(self.run_time) / len(self.run_time)
        return None

    def _json(self, inp):
        try:
            j = json.loads(inp)
            return j
        except: pass
        
        if (m := re.findall(r'```(?:json)?(.*?)```', inp, re.DOTALL)):
            try:
                j = json.loads(m[0])
                return j
            except: pass
        return None

    def __call__(self, *inp):
        n = 0
        while n < self.retry:
            start_t = time.time()
            self.log('inp', inp)
            text = self.prompt(*inp)
            self.log('prompt', text)
            resp = self.llm(text)
            self.log('resp', resp)
            if self.return_json:
                out = self._json(resp)
                self.log('json', out)

                if self.format is not None:
                    if out and all(map(lambda x: x[0] in out and type(out[x[0]]) is x[1], self.format.items())):
                        self.log(f'check {self.format}', '✓')
                    else:
                        self.log(f'check {self.format}', '✗')
                        out = None
            else:
                out = resp

            t = time.time() - start_t
            inout = {
                'id': self.name,
                'timestamp': time.time(),
                'input': text,
                'output': resp,
            }
            self.log('cost time', t)
            if self.lock is not None:
                with self.lock:
                    self.run_time.append(t)
                    self.inout_log.append(inout)
            else:
                self.run_time.append(t)
                self.inout_log.append(inout)
            if out is None:
                n += 1
                self.log('retry', n)
            else:
                break
        return out

    async def async_call(self, *inp):
        n = 0
        while n < self.retry:
            start_t = time.time()
            self.log('inp', inp)
            text = self.prompt(*inp)
            self.log('prompt', text)
            resp = await self.llm(text)
            self.log('resp', resp)
            if self.return_json:
                out = self._json(resp)
                self.log('json', out)

                if self.format is not None:
                    if out and all(map(lambda x: x[0] in out and type(out[x[0]]) is x[1], self.format.items())):
                        self.log(f'check {self.format}', '✓')
                    else:
                        self.log(f'check {self.format}', '✗')
                        out = None
            else:
                out = resp

            t = time.time() - start_t
            inout = {
                'id': self.name,
                'timestamp': time.time(),
                'input': text,
                'output': resp,
            }
            self.log('cost time', t)
            if self.lock is not None:
                with self.lock:
                    self.run_time.append(t)
                    self.inout_log.append(inout)
            else:
                self.run_time.append(t)
                self.inout_log.append(inout)
            if out is None:
                n += 1
                self.log('retry', n)
            else:
                break
        return out

    def __str__(self):
        return f"<{self.__class__.__name__}: {self.name}, prompt: {self.prompt.name}, json: {self.return_json}>"

    def __repr__(self):
        return self.__str__()

class RAGPipe:
    def __init__(self, name, rag=None, verbose=True, return_key=None, lock=None, run_time=None, inout_log=None, **kargs):
        self.name = name
        self.rag = rag
        self.verbose = verbose
        self.return_key = return_key
        self.log = lambda n, t: log.debug(f'[{name}] {n}: {t}') if self.verbose else None

        # multiprocess lock
        self.lock = lock
        self.run_time = run_time if run_time is not None else []
        self.inout_log = inout_log if inout_log is not None else []

    @property
    def time(self):
        if self.run_time:
            return sum(self.run_time) / len(self.run_time)
        return None

    def __call__(self, inp):
        start_t = time.time()
        out = []
        if type(inp) is list:
            self.log('get list', inp)
            inout = []
            for i in inp:
                self.log('inp', i)
                o = self.rag(i)
                self.log('out', o)
                if o is not None and len(o): out.append(o)
                inout.append({
                    'id': self.name,
                    'timestamp': time.time(),
                    'input': i,
                    'output': o,
                })
        else:
            self.log('inp', inp)
            o = self.rag(inp)
            self.log('out', o)
            if o is not None and len(o):
                if self.return_key:
                    o = eval(f'o{self.return_key}')
                    self.log('return_key', o)
                    out = o
                else:
                    out.append(o)
            inout = [{
                'id': self.name,
                'timestamp': time.time(),
                'input': inp,
                'output': o,
            }]

        t = time.time() - start_t
        self.log('cost time', t)
        if self.lock is not None:
            with self.lock:
                self.run_time.append(t)
                self.inout_log.extend(inout)
        else:
            self.run_time.append(t)
            self.inout_log.extend(inout)
        return out

    async def async_call(self, inp):
        start_t = time.time()
        out = []
        if type(inp) is list:
            self.log('get list:', inp)
            inout = []
            for i in inp:
                self.log('inp', i)
                o = await self.rag(i)
                self.log('out', o)
                if o is not None and len(o): out.append(o)
                inout.append({
                    'id': self.name,
                    'timestamp': time.time(),
                    'input': i,
                    'output': o,
                })
        else:
            self.log('inp', inp)
            o = await self.rag(inp)
            self.log('out', o)
            if o is not None and len(o):
                if self.return_key:
                    o = eval(f'o{self.return_key}')
                    self.log('return_key', o)
                    out = o
                else:
                    out.append(o)
            inout = [{
                'id': self.name,
                'timestamp': time.time(),
                'input': inp,
                'output': o,
            }]

        t = time.time() - start_t
        self.log('cost time', t)
        if self.lock is not None:
            with self.lock:
                self.run_time.append(t)
                self.inout_log.extend(inout)
        else:
            self.run_time.append(t)
            self.inout_log.extend(inout)
        return out

    def __str__(self):
        return f"<{self.__class__.__name__}: {self.name}>"

    def __repr__(self):
        return self.__str__()
