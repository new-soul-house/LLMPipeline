import re
import os
import time
import json
import copy
import queue
import asyncio
import datetime
import importlib
import traceback
import collections
from enum import Enum
from pathlib import Path
import multiprocessing as mp
from .log import log
from .pipe import LLMPipe, RAGPipe
from .utils import check_cmd_exist

class State(Enum):
    WAIT = 0
    DONE = 1

class LLMPipeline:
    def __init__(self, pipe, llm_backend, rag_backend, name=None, is_async=False):
        self.pipe = pipe
        self.llm_backend = llm_backend
        self.rag_backend = rag_backend
        self.name = name
        self.is_async = is_async
        self.start_entry = None
        self.pipe_manager = None
        self._check_pipe()
        self._init()

    def _check_pipe(self):
        pipe_names = set(self.pipe.keys())
        conflict_err = 'conflict between the pipe name and the data name'
        for e in self.pipe:
            p = self.pipe[e]
            for i in p.get('inp', []):
                if type(i) is dict:
                    for v in i.values():
                        if v in pipe_names:
                            log.error(f'{conflict_err}: "{i}"')
                            exit()
                else:
                    if i in pipe_names:
                        log.error(f'{conflict_err}: "{i}"')
                        exit()
            
            if (out := p.get('out', None)):
                if (t := type(out)) is str:
                    if out in pipe_names:
                        log.error(f'{conflict_err}: "{out}"')
                        exit()
                elif t is list:
                    for o in out:
                        if o in pipe_names:
                            log.error(f'{conflict_err}: "{out}"')
                            exit()
                elif t is dict:
                    for o in out.values():
                        if o in pipe_names:
                            log.error(f'{conflict_err}: "{out}"')
                            exit()

    def _init(self):
        pipe = self.pipe
        self.exit_pipe = pipe.get('exit', None)
        if 'exit' in pipe: del pipe['exit']

        if not self.is_async:
            self.manager = mp.Manager()
            self.lock = self.manager.Lock()

        pipe_manager = {}
        for e in pipe:
            if 'prompt' in pipe[e]: pipe[e]['mode'] = 'llm'
            elif 'pipe_in_loop' in pipe[e]: pipe[e]['mode'] = 'loop'
            else: pipe[e]['mode'] = 'rag'

            match pipe[e]['mode']:
                case 'llm':
                    if 'llm_backend' in pipe[e]:
                        llm_backend = pipe[e]['llm_backend']
                        del pipe[e]['llm_backend']
                    else:
                        llm_backend = self.llm_backend
                    if self.is_async:
                        pipe_manager[e] = LLMPipe(e, llm=llm_backend, **pipe[e])
                    else:
                        pipe_manager[e] = LLMPipe(e, run_time=self.manager.list(), inout_log=self.manager.list(), llm=llm_backend, lock=self.lock, **pipe[e])
                case 'rag':
                    if 'rag_param' in pipe[e]:
                        param = dict(pipe[e]['rag_param'])
                        rag_backend = lambda x: self.rag_backend(x, **param)
                        del pipe[e]['rag_param']
                    elif 'rag_backend' in pipe[e]:
                        rag_backend = pipe[e]['rag_backend']
                        del pipe[e]['rag_backend']
                    else:
                        rag_backend = self.rag_backend
                    if self.is_async:
                        pipe_manager[e] = RAGPipe(e, rag=rag_backend, **pipe[e])
                    else:
                        pipe_manager[e] = RAGPipe(e, run_time=self.manager.list(), inout_log=self.manager.list(), rag=rag_backend, lock=self.lock, **pipe[e])
        self.pipe_manager = pipe_manager
        log.debug(f"'{self.name}' Pipe manager initialization successful")

        if self.start_entry is None: self._find_start_entry()
        if self.start_entry is None:
            log.error(f"Can't find start entry in pipes.")
            exit()
        log.debug(f"'{self.name}' Start entry: {self.start_entry}")

    def _find_start_entry(self):
        pipe = self.pipe
        
        deps = set()
        for e in pipe:
            deps.update(pipe[e].get('next', []))
            deps.update(pipe[e].get('pipe_in_loop', []))
        
        se = list(set(pipe.keys()) - deps)
        if se: self.start_entry = se

    def pipe2mermaid(self, pipes, info=None):
        pipe = copy.deepcopy(pipes)
        mermaid = 'graph TD\n'
        indent = ' '*4
        def_dict = {
            'data': {
                'style': 'fill:#9BCFB8,color:black',
                'shape': lambda x: f'{x}(["{x}"])',
                'item': set(),
            },
            'llm': {
                'style': 'fill:#ECE4E2,color:black',
                'shape': lambda x: f'{x}["{x}"]',
                'item': set(),
            },
            'rag': {
                'style': 'fill:#FE929F,color:black',
                'shape': lambda x: f'{x}("{x}")',
                'item': set(),
            },
            'loop': {
                'style': 'fill:#CC8A4D,color:black',
                'shape': lambda x: f'{x}(("{x}"))',
                'item': set(),
            },
            'exit': {
                'style': 'fill:#3D3E3F,color:white',
                'shape': lambda x: f'{x}[["{x}"]]',
                'item': ['exit'],
            },
        }

        defines = []
        # todo: here can from start_entry
        for e in pipe:
            m = pipe[e]['mode']
            def_dict[m]['item'].add(e)
            if m == 'loop': def_dict[m]['item'].add(f'{e}_done')

            inp = pipe[e]['inp']
            if type(inp) is str:
                def_dict['data']['item'].add(inp)
            elif type(inp) is list:
                for i in inp:
                    if type(i) is dict:
                        inp.remove(i)
                        inp += list(i.values())
                def_dict['data']['item'].update(inp)

            o = pipe[e].get('out', None)
            if type(o) is str:
                def_dict['data']['item'].add(o)
            elif type(o) is list:
                def_dict['data']['item'].update(o)
            elif type(o) is dict:
                def_dict['data']['item'].update(o.values())
        for d in def_dict.values():
            defines += [d['shape'](i) for i in d['item']]

        # bfs
        links = set()
        items = self.start_entry[:]
        while items:
            e = items.pop(0)
            if e == 'exit': continue
            if pipe[e]['mode'] == 'loop':
                inp = pipe[e]['inp'][0]
                links.add(f'{inp} ==> {e}')
                loop_inps = set()
                loop_outs = set()
                for i in pipe[e]['pipe_in_loop']:
                    if inp in pipe[i]['inp']:
                        pipe[i]['inp'][pipe[i]['inp'].index(inp)] = e
                    items.append(i)
                    loop_inps.update(pipe[i]['inp'])
                    if type(pipe[i]['out']) is dict:
                        loop_outs.update(pipe[i]['out'].values())
                    if type(pipe[i]['out']) is list:
                        loop_outs.update(pipe[i]['out'])
                    elif type(pipe[i]['out']) is str:
                        loop_outs.add(pipe[i]['out'])
                
                l_out = ' & '.join(loop_outs - loop_inps)
                outs = f'{e}_done'
                links.add(f'{l_out} ==> {outs}')
            else:
                inps = ' & '.join(pipe[e]['inp'])
                o = pipe[e]['out']
                if (t := type(o)) is str:
                    outs = o
                elif t is list:
                    outs = ' & '.join(o)
                elif t is dict:
                    outs = ' & '.join(o.values())
                if info:
                    t = f'{info["detail"][e]["avg_time"]:.2f}s'
                    link = f'{inps} --> {e} -.->|{t}| {outs}'
                else:
                    link = f'{inps} --> {e} -.-> {outs}'
                links.add(link)

            for n in pipe[e].get('next', []):
                if n == 'exit':
                    if info:
                        t = f'{info["total_time"]:.2f}s'
                        links.add(f'{outs} --o|{t}| exit')
                    else:
                        links.add(f'{outs} --o exit')
                else:
                    items.append(n)

        for i in defines+list(links):
            mermaid += f'{indent}{i}\n'

        # add style
        for k, d in def_dict.items():
            if d['item']:
                mermaid += f'{indent}classDef {k.upper()} {d["style"]}\n'
                mermaid += f'{indent}class {",".join(d["item"])} {k.upper()}\n'

        return mermaid

    def perf2mermaid(self, perf, pipe):
        mermaid = 'gantt\ntitle Task Timeline\ndateFormat  x\naxisFormat  %M:%S.%L\n'
        base_time = perf[0][2]
        data = collections.defaultdict(list)
        loop_end = {}
        for name, e, start_time, end_time in perf:
            if 'pid' in name:
                arr = name.split(': ')
                n = f'{arr[0]}_{int(arr[1]):0>2d}'
            else:
                n = name
            s = (start_time - base_time) * 1000
            Δ = (end_time - start_time) * 1000
            if e in pipe:
                if pipe[e]['mode'] == 'loop':
                    loop_end[f'{e}_end'] = (n, e, s)
                else:
                    data[n].append((e, s, Δ))
            elif e in loop_end:
                n, e, s_ = loop_end[e]
                Δ_ = s + Δ - s_
                data[n].append((e, s_, Δ_))
        
        for k in sorted(data.keys()):
            mermaid += f'section {k}\n'
            for e, s, Δ in data[k]:
                if pipe[e]['mode'] == 'loop':
                    mermaid += f'{e}: done, {s:.0f}, {Δ:.0f}ms\n'
                else:
                    mermaid += f'{e}: {s:.0f}, {Δ:.0f}ms\n'

        return mermaid

    def gen_info(self, data, perf, start_t, save_pref=False):
        pipe_manager = self.pipe_manager

        info = {
            'perf': perf,
            'detail': {},
            'total_time': time.time()-start_t,
            'mermaid': {},
        }
        for k in sorted(pipe_manager, key=lambda k: pipe_manager[k].time or -1):
            info['detail'][k] = {
                # 'run_time': list(pipe_manager[k].run_time),
                'avg_time': pipe_manager[k].time,
            }

        if save_pref and 'error_msg' not in data:
            info['mermaid']['pipe'] = self.pipe2mermaid(self.pipe, info)
            info['mermaid']['perf'] = self.perf2mermaid(perf, self.pipe)
            fname = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
            if check_cmd_exist('mmdc'):
                pipe_img = f'logs/{fname}_pipe.png'
                os.popen(f'echo "{info["mermaid"]["pipe"]}" | mmdc -o {pipe_img}')
                log.debug(f'save {pipe_img}')
                perf_img = f"logs/{fname}_perf.png"
                os.popen(f'echo "{info["mermaid"]["perf"]}" | mmdc -o {perf_img}')
                log.debug(f'save {perf_img}')
                md_pipe = f"![pipe_img]({pipe_img.split('/')[1]})"
                md_perf = f"![perf_img]({perf_img.split('/')[1]})"
            else:
                log.warning('Please install mmdc to generate mermaid images.')
                md_pipe = f"```mermaid\n{info['mermaid']['pipe']}```"
                md_perf = f"```mermaid\n{info['mermaid']['perf']}```"

            r_str = f'```json\n{json.dumps(data, indent=4, ensure_ascii=False)}\n```'
            md_content = f'## result\n{r_str}\n## Pipeline\n{md_pipe}\n## Perfermence\n{md_perf}'
            md_file = f'logs/{fname}_report.md'
            with open(md_file, 'w') as f: f.write(md_content)

        log.debug(f'pipe detail:\n{json.dumps(info, indent=4, ensure_ascii=False)}')
        info['logs'] = []
        for k in pipe_manager:
            info['logs'] += pipe_manager[k].inout_log
        
        return info

    def reformat_return(self, data):
        if 'error_msg' not in data and self.exit_pipe is not None:
            ret = {}
            for k, v in self.exit_pipe.items():
                if type(v) is str:
                    d = data
                    for i in v.split('.'): d = d[i]
                    ret[k] = d
                elif type(v) is list and type(v[0]) is dict:
                    d = []
                    for i in range(len(data[list(v[0].values())[0]])):
                        t = {}
                        for m, n in v[0].items():
                            t[m] = data[n][i]
                        d.append(t)
                    ret[k] = d
            return ret
        return data

    def task_process(self, pid, task_queue, perf_queue, pipe_manager, data, lock):
        name = f'pid: {pid}'
        log.debug(f'{name}, start')

        try:
            while True:
                start_time = time.time()
                try:
                    entry, pipes = task_queue.get_nowait()
                    # log.debug(f'{name}, get entry: {entry}')
                    # time.sleep(5)
                    if entry == 'exit':
                        # if task_queue.qsize() == 0:
                        task_queue.put((entry, pipes))
                        log.debug(f'{name}, exit')
                        break
                        # else: continue
                except queue.Empty:
                    # log.debug(f'{name}, queue empty, wait new task ...')
                    # time.sleep(5)
                    # break
                    continue

                param = pipes[entry]
                match param['mode']:
                    case 'llm':
                        pipe = pipe_manager[entry]
                    case 'rag':
                        pipe = pipe_manager[entry]
                    case 'loop':
                        loop_item = param['inp'][0]
                        with lock: data[entry] = {loop_item: data[loop_item]}
                        n = len(data[loop_item])

                        for i, item in enumerate(data[loop_item]):
                            nps = copy.deepcopy(pipes)

                            for nt in param['pipe_in_loop']:
                                nps[nt]['loop'] = entry
                                nps[nt]['loop_index'] = i
                                o = nps[nt]['out']
                                with lock:
                                    if type(o) is str:
                                        pre = data[entry]
                                        pre[o] = [State.WAIT] * n
                                        data[entry] = pre
                                    elif type(o) is list:
                                        for j in o:
                                            pre = data[entry]
                                            pre[j] = [State.WAIT] * n
                                            data[entry] = pre
                                    elif type(o) is dict:
                                        for j in o.values():
                                            pre = data[entry]
                                            pre[j] = [State.WAIT] * n
                                            data[entry] = pre

                                task_queue.put((nt, nps))

                        loop_end_entry = f'{entry}_end'
                        pipes |= {loop_end_entry: {
                            'mode': 'loop_end',
                            'loop': entry,
                            'next': param['next'],
                        }}
                        task_queue.put((loop_end_entry, pipes))
                        perf_queue.put((name, entry, start_time, time.time()))
                        continue
                    case 'loop_end':
                        has_done = []
                        for v in data[param['loop']].values():
                            has_done.append(all([i is not State.WAIT for i in v]))

                        if all(has_done):
                            loop_data = data[param['loop']]
                            with lock:
                                for k,v in loop_data.items():
                                    if k not in data: data[k] = v
                                del data[param['loop']]

                            if 'next' in param:
                                for e in param['next']:
                                    task_queue.put((e, pipes))
                            perf_queue.put((name, entry, start_time, time.time()))
                        else:
                            task_queue.put((entry, pipes))
                        continue

                if 'loop' in param:
                    has_inp = []
                    for i in param['inp']:
                        if type(i) is str:
                            has_inp.append(i in data or (i in data[param['loop']] and data[param['loop']][i][param['loop_index']] is not State.WAIT))
                        elif type(i) is dict:
                            for j in i.values():
                                has_inp.append(j in data or (j in data[param['loop']] and data[param['loop']][j][param['loop_index']] is not State.WAIT))

                    if all(has_inp):
                        inps = []
                        for i in param['inp']:
                            if type(i) is str:
                                if i in data[param['loop']]:
                                    inps.append(data[param['loop']][i][param['loop_index']])
                                else:
                                    inps.append(data[i])
                            elif type(i) is dict:
                                d = {}
                                for k, v in i.items():
                                    if v in data[param['loop']]:
                                        d[k] = data[param['loop']][v][param['loop_index']]
                                    else:
                                        d[k] = data[v]
                                inps.append(d)

                        out = pipe(*inps)
                        if type(param['out']) is str:
                            with lock:
                                pre = data[param['loop']]
                                pre[param['out']][param['loop_index']] = out
                                data[param['loop']] = pre
                        elif type(param['out']) is list:
                            with lock:
                                pre = data[param['loop']]
                                for k in param['out']:
                                    pre[k][param['loop_index']] = out[k]
                                data[param['loop']] = pre
                        elif type(param['out']) is dict:
                            with lock:
                                pre = data[param['loop']]
                                for k in param['out']:
                                    pre[param['out'][k]][param['loop_index']] = out[k]
                                data[param['loop']] = pre

                        if 'next' in param:
                            for e in param['next']:
                                task_queue.put((e, pipes))
                        perf_queue.put((name, entry, start_time, time.time()))
                    else:
                        task_queue.put((entry, pipes))
                else:
                    has_inp = all(i in data for i in param['inp'])
                    if has_inp:
                        inps = []
                        for i in param['inp']:
                            if type(i) is str:
                                inps.append(data[i])
                            elif type(i) is dict:
                                inps.append({k:data[v] for k, v in i.items()})

                        out = pipe(*inps)
                        if type(param['out']) is str:
                            with lock:
                                data[param['out']] = out
                        elif type(param['out']) is list:
                            with lock:
                                for k in param['out']:
                                    data[k] = out[k]
                        elif type(param['out']) is dict:
                            with lock:
                                for k in param['out']:
                                    data[param['out'][k]] = out[k]

                        if 'next' in param:
                            for e in param['next']:
                                task_queue.put((e, pipes))
                        perf_queue.put((name, entry, start_time, time.time()))
                    else:
                        task_queue.put((entry, pipes))
        except Exception as e:
            error_msg = traceback.format_exc()
            with lock: data['error_msg'] = error_msg
            log.error(f'[{name}]:\n{error_msg}')
            task_queue.put(('exit', {}))
            log.debug(f'{name}, exit')

    def mp_run(self, data, core_num=4, save_pref=False):
        pipe = copy.deepcopy(self.pipe)
        pipe_manager, lock = self.pipe_manager, self.lock
        start_t = time.time()
        task_queue = self.manager.Queue()
        perf_queue = self.manager.Queue()
        result = self.manager.dict()
        for k, v in data.items(): result[k] = v

        for se in self.start_entry: task_queue.put((se, pipe))
        processes = []
        for i in range(core_num):
            p = mp.Process(target=self.task_process, args=(i, task_queue, perf_queue, pipe_manager, result, lock))
            processes.append(p)
            p.start()
        for p in processes: p.join()

        r = dict(result)
        log.debug(f'final out:\n{json.dumps(r, indent=4, ensure_ascii=False)}')

        perf = []
        while not perf_queue.empty(): perf.append(perf_queue.get())
        info = self.gen_info(r, perf, start_t, save_pref)

        return self.reformat_return(r), info

    async def async_task(self, pipe_name, queue, result, perf):
        start_time = time.time()
        log.banner(f"Enter async task: {pipe_name}")
        pipe = self.pipe[pipe_name]
        p_name = pipe_name

        if 'pipe_in_loop' in pipe:
            loop_item = pipe['inp'][0]
            d = await queue[loop_item].get()
            queue[loop_item].put_nowait(d)
            n = len(d)

            loop_out_items = []
            for pn in pipe['pipe_in_loop']:
                o = self.pipe[pn]['out']

                if type(o) is str:
                    loop_out_items.append(o)
                elif type(o) is list:
                    loop_out_items += o
                elif type(o) is dict:
                    for k in o:
                        loop_out_items.append(o[k])

            for item in [loop_item]+loop_out_items:
                for i in range(n):
                    t = f'#{pipe_name}#_{i}_[{item}]'
                    queue[t] = asyncio.Queue()
                    if item == loop_item: queue[t].put_nowait(d[i])

            tasks = []
            for pn in pipe['pipe_in_loop']:
                for i in range(n):
                    new_name = f'{pipe_name} -> {pn} ({i})'
                    new_pipe = copy.copy(self.pipe[pn])

                    new_inps = []
                    for inp in new_pipe['inp']:
                        if type(inp) is str:
                            if inp == loop_item or inp in loop_out_items:
                                new_inps.append(f'#{pipe_name}#_{i}_[{inp}]')
                            else:
                                new_inps.append(inp)
                        elif type(inp) is dict:
                            t = {}
                            for k, v in inp.items():
                                if v == loop_item or v in loop_out_items:
                                    t[k] = f'#{pipe_name}#_{i}_[{v}]'
                                else: t[k] = v
                            new_inps.append(t)
                    new_pipe['inp'] = new_inps

                    o = new_pipe['out']
                    if type(o) is str:
                        new_pipe['out'] = f'#{pipe_name}#_{i}_[{o}]'
                    elif type(o) is list:
                        new_pipe['out'] = [f'#{pipe_name}#_{i}_[{item}]' for item in o]
                    elif type(o) is dict:
                        new_pipe['out'] = {k:f'#{pipe_name}#_{i}_[{o[k]}]' for k in o}

                    self.pipe[new_name] = new_pipe

                    task = asyncio.create_task(self.async_task(new_name, queue, result, perf))
                    tasks.append(task)
            await asyncio.gather(*tasks)

            # Delete intermediate process data
            for pn in pipe['pipe_in_loop']:
                for i in range(n):
                    new_name = f'{pipe_name} -> {pn} ({i})'
                    del self.pipe[new_name]

            for item in [loop_item]+loop_out_items:
                d = []
                for i in range(n):
                    t = f'#{pipe_name}#_{i}_[{item}]'
                    del queue[t]
                    if t in result:
                        d.append(result[t])
                        del result[t]

                if item not in result:
                    result[item] = d
                    queue[item] = asyncio.Queue()
                    queue[item].put_nowait(d)
        else:
            inps = []
            for i in pipe['inp']:
                if type(i) is str:
                    d = await queue[i].get()
                    inps.append(d)
                    queue[i].put_nowait(d)
                elif type(i) is dict:
                    t = {}
                    for k, v in i.items():
                        d = await queue[v].get()
                        t[k] = d
                        queue[v].put_nowait(d)
                    inps.append(t)

            if '-> ' in pipe_name and pipe_name[-1] == ')':
                p_name = pipe_name.split('-> ')[1].split(' (')[0]

            out = await self.pipe_manager[p_name].async_call(*inps)

            o = pipe['out']
            if type(o) is str:
                result[o] = out
                if o not in queue: queue[o] = asyncio.Queue()
                queue[o].put_nowait(out)
            elif type(o) is list:
                for k in o:
                    k_ = k
                    if k[0] == '#' and k[-1] == ']':
                        k_ = k.split('_[')[1][:-1]
                    result[k] = out[k_]
                    if k not in queue: queue[k] = asyncio.Queue()
                    queue[k].put_nowait(out[k_])
            elif type(o) is dict:
                for k in o:
                    result[o[k]] = out[k]
                    if o[k] not in queue: queue[o[k]] = asyncio.Queue()
                    queue[o[k]].put_nowait(out[k])

        log.banner(f"Leave async task: {pipe_name}")
        perf.append(('coroutine', p_name, start_time, time.time()))

    async def async_run(self, data, save_pref=False):
        start_t = time.time()
        # find outloop pipes
        inloop_pipes = set()
        for pipe_name in self.pipe:
            if 'pipe_in_loop' in self.pipe[pipe_name]:
                inloop_pipes |= set(self.pipe[pipe_name]['pipe_in_loop'])
        outloop_pipes = set(self.pipe.keys()) - inloop_pipes

        # init queue
        asyncio_queue = {}
        for pipe_name in outloop_pipes:
            for i in self.pipe[pipe_name]['inp']:
                if type(i) is str:
                    asyncio_queue[i] = asyncio.Queue()
                elif type(i) is dict:
                    for v in i.values():
                        asyncio_queue[v] = asyncio.Queue()
        # put data into queue
        for k, v in data.items():
            if k in asyncio_queue: asyncio_queue[k].put_nowait(v)

        perf = []
        tasks = []
        for pipe_name in outloop_pipes:
            task = asyncio.create_task(self.async_task(pipe_name, asyncio_queue, data, perf))
            tasks.append(task)
        await asyncio.gather(*tasks)
        log.debug(f'final out:\n{json.dumps(data, indent=4, ensure_ascii=False)}')

        info = self.gen_info(data, perf, start_t, save_pref)
        return self.reformat_return(data), info

    @property
    def run(self):
        if self.is_async:
            log.debug(f"Run '{self.name}' pipeline in coroutine")
            return self.async_run
        else:
            log.debug(f"Run '{self.name}' pipeline in multiprocess")
            return self.mp_run

class PipelineManager:
    def __init__(self, pipes_dir, prompt_manager, llm_client=None, rag_client=None, is_async=False):
        log.debug('Setup PipelineManager')
        if pipes_dir is None:
            log.debug('PipelineManager dir is None')
        else:
            self.pipes_dir = Path(pipes_dir)
            self.prompt_manager = prompt_manager
            self.llm_client = llm_client
            self.rag_client = rag_client
            self.is_async = is_async
            self.pipes = {}
            self.load_pipes()

    def load_pipes(self):
        self.pipes = {}
        log.debug(f'Start load pipelines: {self.pipes_dir}')
        pipe_files = list(self.pipes_dir.glob('*_pipe.py'))
        log.debug(f'Find {len(pipe_files)} pipeline files: {[p.stem for p in pipe_files]}')

        for pf in pipe_files:
            m = importlib.import_module(f'{str(self.pipes_dir).replace("/",".")}.{pf.stem}')
            conf = copy.deepcopy(m.pipe)
            pipe = copy.deepcopy(m.pipe)
            for k in pipe:
                if 'prompt' in pipe[k]:
                    pipe[k]['prompt'] = self.prompt_manager.prompts[pipe[k]['prompt']]

            self.pipes[pf.stem] = {
                'file': pf,
                'conf': conf,
                'func': LLMPipeline(pipe, self.llm_client, self.rag_client, pf.stem, self.is_async)
            }

        log.debug('All pipelines loaded')

    def export_pipe_conf(self):
        conf = {k: copy.deepcopy(v['conf']) for k,v in self.pipes.items()}
        for c in conf.values():
            for pipe_conf in c.values():
                if 'format' in pipe_conf:
                    for k, v in pipe_conf['format'].items():
                        pipe_conf['format'][k] = str(v)
        return conf

    def update_pipe(self, pipe_name, pipe_data):
        if pipe_name.endswith('_pipe'):
            pipe_file = self.pipes_dir / f'{pipe_name}.py'

            try:
                content = json.dumps(pipe_data, indent=4, ensure_ascii=False)
                content = re.sub(r'"<class \'(.*)\'>"', r'\1', content)

                conf = pipe_data
                for pipe_conf in conf.values():
                    if 'format' in pipe_conf:
                        for k, v in pipe_conf['format'].items():
                            pipe_conf['format'][k] = eval(v.replace("<class '","").replace("'>",""))

                pipe = copy.deepcopy(conf)
                for k in pipe:
                    if 'prompt' in pipe[k]:
                        pipe[k]['prompt'] = self.prompt_manager.prompts[pipe[k]['prompt']]

                self.pipes[pipe_name] = {
                    'file': pipe_file,
                    'conf': conf,
                    'func': LLMPipeline(pipe, self.llm_client, self.rag_client)
                }

                with open(pipe_file, 'w') as f:
                    content = 'pipe = ' + content + '\n'
                    f.write(content)
                
                log.debug(f'Save pipeline "{pipe_name}":\n{content}')
                return f'Successfully saved {pipe_name}'
            except Exception as e:
                return f'Error: {e}'
        else:
            return 'Error: name must end with `_pipe`.'
