import re
import os
import time
import json
import copy
import queue
import datetime
import collections
import multiprocessing as mp
from .log import log
from .pipe import LLMPipe, RAGPipe
from .utils import check_cmd_exist

class LLMPipeline:
    def __init__(self, pipe, data, llm_backend, rag_backend):
        self.pipe = pipe
        self.data = data
        self.llm_backend = llm_backend
        self.rag_backend = rag_backend
        self._check_pipe()
    
    def _check_pipe(self):
        pipe_names = set(self.pipe.keys())
        conflict_err = 'conflict between the pipe name and the data name'
        for e in self.pipe:
            p = self.pipe[e]
            for i in p.get('inp', []):
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

    def pipe2mermaid(self, start_entry, pipes, info=None):
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
        items = [start_entry]
        while items:
            e = items.pop(0)
            if e == 'exit': continue
            if pipe[e]['mode'] == 'loop':
                inp = pipe[e]['inp']
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
            arr = name.split(': ')
            n = f'{arr[0]}_{int(arr[1]):0>2d}'
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

    def task_process(self, pid, task_queue, perf_queue, pipe_manager, data, lock):
        name = f'pid: {pid}'
        log.debug(f'{name}, start')

        while True:
            start_time = time.time()
            try:
                entry, pipes = task_queue.get_nowait()
                # log.debug(f'{name}, get entry: {entry}')
                if entry == 'exit':
                    if task_queue.qsize() == 0:
                        task_queue.put((entry, pipes))
                        break
                    else: continue
            except queue.Empty:
                # log.debug(f'{name}, queue empty, wait new task ...')
                # break
                continue

            param = pipes[entry]
            match param['mode']:
                case 'llm':
                    pipe = pipe_manager[entry]
                case 'rag':
                    pipe = pipe_manager[entry]
                case 'loop':
                    with lock: data[entry] = {param['inp']: data[param['inp']]}
                    n = len(data[param['inp']])

                    for i, item in enumerate(data[param['inp']]):
                        nps = copy.deepcopy(pipes)

                        for nt in param['pipe_in_loop']:
                            nps[nt]['loop'] = entry
                            nps[nt]['loop_index'] = i
                            o = nps[nt]['out']
                            with lock:
                                if type(o) is str:
                                    pre = data[entry]
                                    pre[o] = [None] * n
                                    data[entry] = pre
                                elif type(o) is list:
                                    for j in o:
                                        pre = data[entry]
                                        pre[j] = [None] * n
                                        data[entry] = pre
                                elif type(o) is dict:
                                    for j in o.values():
                                        pre = data[entry]
                                        pre[j] = [None] * n
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
                        has_done.append(all([i is not None for i in v]))

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
                        has_inp.append(i in data or (i in data[param['loop']] and data[param['loop']][i][param['loop_index']] is not None))
                    elif type(i) is dict:
                        for j in i.values():
                            has_inp.append(j in data or (j in data[param['loop']] and data[param['loop']][j][param['loop_index']] is not None))

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

    def run(self, start_entry, core_num=4, save_pref=False):
        pipe, data = self.pipe, self.data
        start_t = time.time()
        manager = mp.Manager()
        task_queue = manager.Queue()
        perf_queue = manager.Queue()
        lock = manager.Lock()
        result = manager.dict()
        for k, v in data.items(): result[k] = v

        pipe_manager = {}
        for e in pipe:
            match pipe[e]['mode']:
                case 'llm':
                    if 'llm_backend' in pipe[e]:
                        llm_backend = pipe[e]['llm_backend']
                        del pipe[e]['llm_backend']
                    else:
                        llm_backend = self.llm_backend
                    pipe_manager[e] = LLMPipe(e, run_time=manager.list(), llm=llm_backend, lock=lock, **pipe[e])
                case 'rag':
                    if 'rag_backend' in pipe[e]:
                        rag_backend = pipe[e]['rag_backend']
                        del pipe[e]['rag_backend']
                    else:
                        rag_backend = self.rag_backend
                    pipe_manager[e] = RAGPipe(e, run_time=manager.list(), rag=rag_backend, lock=lock, **pipe[e])

        task_queue.put((start_entry, pipe))
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

        info = {
            'perf': perf,
            'detail': {},
            'total_time': time.time()-start_t,
            'mermaid': {},
        }
        for k in sorted(pipe_manager, key=lambda k: pipe_manager[k].time or -1):
            info['detail'][k] = {
                'run_time': list(pipe_manager[k].run_time),
                'avg_time': pipe_manager[k].time,
            }

        if save_pref:
            info['mermaid']['pipe'] = self.pipe2mermaid(start_entry, pipe, info)
            info['mermaid']['perf'] = self.perf2mermaid(perf, pipe)
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

            r_str = f'```json\n{json.dumps(r, indent=4, ensure_ascii=False)}\n```'
            md_content = f'## result\n{r_str}\n## Pipeline\n{md_pipe}\n## Perfermence\n{md_perf}'
            md_file = f'logs/{fname}_report.md'
            with open(md_file, 'w') as f: f.write(md_content)

        log.debug(f'pipe detail:\n{ json.dumps(info, indent=4, ensure_ascii=False)}')

        # breakpoint()
        return r, info
