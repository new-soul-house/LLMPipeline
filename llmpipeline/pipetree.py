import copy
import time
import queue
import asyncio
import importlib
import traceback
import collections
from enum import Enum
from pathlib import Path
import multiprocessing as mp
from .log import log
from .prompt import Prompt
from .pipe import LLMPipe, RAGPipe

class Data:
    mermaid_style = 'fill:#9BCFB8,color:black'
    mermaid_shape = lambda x: f'{x}(["{x}"])'

class DataState(Enum):
    VOID = 0

class Node:
    mermaid_style = 'color:black'
    mermaid_shape = lambda x: f'{x}["{x}"]'

    def __init__(self, name, conf, tree=None):
        self.name = name
        self.conf = conf
        self.tree = tree
        self.run_cnt = 0
        self.in_loop = None
        self.next = []
        self.loop_nodes = []
        self.reset_out_flag = 'reset_out' in self.conf
        if self.reset_out_flag:
            self.conf['out'] = self.conf['reset_out']
            del self.conf['reset_out']
        self.set_mermaid()
        self.post_init()

    def set_mermaid(self):
        self.mermaid_inps = []
        if 'inp' in self.conf:
            for i in self.conf['inp']:
                if (t := type(i)) is str:
                    self.mermaid_inps.append(i)
                elif t is dict:
                    self.mermaid_inps += list(i.values())

        outs = []
        if (o := self.conf.get('out', None)):
            if (t := type(o)) is str:
                outs = [o]
            elif t is list:
                outs = o[:]
            elif t is dict:
                outs = list(o.values())
        self.mermaid_outs = outs
        self.mermaid_data = self.mermaid_inps + self.mermaid_outs

    def get_mermaid(self, info=None):
        inps = ' & '.join(self.mermaid_inps)
        outs = ' & '.join(self.mermaid_outs)

        defines = [self.__class__.mermaid_shape(self.name)] + [Data.mermaid_shape(d) for d in self.mermaid_data]

        t = info["detail"][self.name]["avg_time"] if info else None
        t = f'|{t:.2f}s|' if t is not None else ''
        inout_link = f'{inps} --> {self.name} -.->{t} {outs}'

        links = [inout_link]
        for n in self.next:
            if n.name == 'exit':
                t = f'|total: {info["total_time"]:.2f}s|' if info and self.name in info['exec_path'] else ''
                links.append(f'{outs} --o{t} exit')

        return defines, links

    def update(self, nodes):
        for name in self.conf.get('next', []):
            if name in nodes: self.next.append(nodes[name])

    def post_init(self):
        pass

    def reset(self):
        self.run_cnt = 0

    def get_inps_mp(self, data, config=None):
        def get_data(i):
            if i not in data: return DataState.VOID
            if type(data[i]) is list:
                if config and i in config['loop_index']:
                    loop_i = config['loop_index'][i]
                    return data[i][loop_i]
                elif DataState.VOID in data[i]:
                    return DataState.VOID
            return data[i]

        inps = []
        for i in self.conf['inp']:
            if type(i) is str:
                if (d := get_data(i)) is DataState.VOID: return []
                else: inps.append(d)
            elif type(i) is dict:
                t = {}
                for k, v in i.items():
                    if (d := get_data(v)) is DataState.VOID: return []
                    else: t[k] = d
                inps.append(t)
        return inps

    def current_mp_task(self, inps, data, queue, config=None):
        if self.__class__.__name__ in ['LLMNode', 'RAGNode']:
            out = self.pipe(*inps)
            self.set_out(out, data, config=config)

        for n in self.next: queue.put((n.name, config))

    def mp_run(self, mp_name, data, queue, perf, config=None):
        if (inps := self.get_inps_mp(data, config)):
            start_time = time.time()
            self.run_cnt += 1
            cnt = self.run_cnt
            log.banner(f"Enter mp task: {self.name}, cnt: {cnt}, {mp_name}")
            self.current_mp_task(inps, data, queue, config)
            log.banner(f"Leave mp task: {self.name}, cnt: {cnt}, {mp_name}")
            perf.put((mp_name, self.name, start_time, time.time()))
        else:
            queue.put((self.name, config))

    async def get_inps(self, queue):
        inps = []
        for i in self.conf['inp']:
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
        return inps

    def set_out(self, out, data, queue=None, config=None):
        def set_data(k, v, config, queue):
            if config:
                with self.tree.mp_lock:
                    i = config['loop_index'][k]
                    pre = data[k]
                    pre[i] = v
                    data[k] = pre
            else:
                data[k] = v

            if queue:
                arr = [queue]
                while arr:
                    q = arr.pop(0)
                    q[k].put_nowait(v)
                    if '_sub' in q: arr += q['_sub']

        o = self.conf['out']
        if (t := type(o)) is str:
            set_data(o, out, config, queue)
        elif t is list:
            for k in o:
                set_data(k, out[k], config, queue)
        elif t is dict:
            for k in o:
                set_data(o[k], out[k], config, queue)

    def reset_out(self, queue):
        def q_del(q, k):
            if k in q:
                while not q[k].empty(): q[k].get_nowait()
            if '_sub' in q:
                for sub_q in q['_sub']: q_del(sub_q, k)

        o = self.conf['out']
        if (t := type(o)) is str:
            q_del(queue, o)
        elif t is list:
            for k in o: q_del(queue, k)
        elif t is dict:
            for k in o: q_del(queue, o[k])

    async def add_task(self, data, queue, dynamic_tasks):
        for n in self.next:
            task = asyncio.create_task(n.run(data, queue, dynamic_tasks), name=n.name)
            dynamic_tasks.append(task)

    async def current_task(self, data, queue, dynamic_tasks):
        if self.__class__.__name__ in ['LLMNode', 'RAGNode']:
            inps = await self.get_inps(queue)
            out = await self.pipe.async_call(*inps)
            self.set_out(out, data, queue)

    async def async_run(self, data, queue, dynamic_tasks):
        start_time = time.time()
        self.run_cnt += 1
        cnt = self.run_cnt
        log.banner(f"Enter async task: {self.name}, cnt: {cnt}")
        if self.reset_out_flag: self.reset_out(queue)
        await self.add_task(data, queue, dynamic_tasks)
        await self.current_task(data, queue, dynamic_tasks)
        log.banner(f"Leave async task: {self.name}, cnt: {cnt}")
        self.tree.perf.append(('coroutine', self.name, start_time, time.time()))

    @property
    def run(self):
        if self.tree.is_async:
            return self.async_run
        else:
            return self.mp_run

    def export_as_comfyui(self):
        return {}

    def __str__(self):
        return f"<{self.__class__.__name__}: {self.name}, next: {[n.name for n in self.next]}>"

    def __repr__(self):
        return self.__str__()

class LLMNode(Node):
    mermaid_style = 'fill:#ECE4E2,color:black'
    mermaid_shape = lambda x: f'{x}["{x}"]'

    def post_init(self):
        tree = self.tree
        self.conf['prompt'] = tree.prompt_manager.get(self.conf['prompt'])
        if tree.is_async:
            pipe = LLMPipe(self.name, llm=tree.llm_backend, **self.conf)
        else:
            pipe = LLMPipe(
                    self.name,
                    llm=tree.llm_backend,
                    lock=tree.mp_lock,
                    run_time=tree.mp_manager.list(),
                    inout_log=tree.mp_manager.list(),
                    **self.conf
                    )
        tree.pipe_manager[self.name] = pipe
        self.pipe = pipe

    def export_as_comfyui(self):
        inps = {i:["TEXT"] for i in self.pipe.prompt.keys}
        opt_inps = {"模型": ["MODEL"]}
        prompt = {
            "prompt": [
                "STRING",
                {"default": self.pipe.prompt.text, "multiline": True, "dynamicPrompts": True}
            ]
        }
        outs = self.mermaid_outs
        d = {
            "input": {
                "required": inps | prompt,
                "optional": opt_inps
            },
            "input_order": {"required": self.pipe.prompt.keys},
            "output": ["TEXT"] * len(outs),
            "output_is_list": [False] * len(outs),
            "output_name": outs,
            "name": self.name,
            "display_name": self.name,
            "description": f"{self.name} prompt",
            "python_module": "nodes",
            "category": "提示词",
            "output_node": False,
        }
        return {self.name: d}

class RAGNode(Node):
    mermaid_style = 'fill:#FE929F,color:black'
    mermaid_shape = lambda x: f'{x}("{x}")'

    def post_init(self):
        tree = self.tree
        if (param := self.conf.get('rag_param', None)):
            rag_backend = lambda x: tree.rag_backend(x, **dict(param))
        else:
            rag_backend = tree.rag_backend

        if tree.is_async:
            pipe = RAGPipe(self.name, rag=rag_backend, **self.conf)
        else:
            pipe = RAGPipe(
                    self.name,
                    rag=rag_backend,
                    lock=tree.mp_lock,
                    run_time=tree.mp_manager.list(),
                    inout_log=tree.mp_manager.list(),
                    **self.conf
                    )
        tree.pipe_manager[self.name] = pipe
        self.pipe = pipe

    def export_as_comfyui(self):
        param = self.conf.get('rag_param', {})
        inps = {
            "text": ["TEXT"],
            "kb": ["STRING", {
                "default": param.get('kb_id', None),
                "multiline": False,
                "dynamicPrompts": True
            }],
            "top_k": ["INT", {
                "default": param.get('top_k', 1),
                "min": 1
            }],
            "threshold": ["FLOAT", {
                "default": param.get('threshold', 0.5),
                "min": 0.01,
                "max": 1.0,
                "step": 0.1
            }]
        }
        opt_inps = {}
        outs = self.mermaid_outs
        d = {
            "input": {
                "required": inps,
                "optional": opt_inps
            },
            "input_order": {"required": list(inps.keys())},
            "output": ["TEXT"] * len(outs),
            "output_is_list": [False] * len(outs),
            "output_name": outs,
            "name": self.name,
            "display_name": self.name,
            "description": f"{self.name} rag search",
            "python_module": "nodes",
            "category": "知识库",
            "output_node": False,
        }
        return {self.name: d}

class LoopNode(Node):
    mermaid_style = 'fill:#CC8A4D,color:black'
    mermaid_shape = lambda x: f'{x}(("{x}"))'

    def update(self, nodes):
        super().update(nodes)

        self.loop_nodes = []
        for name in self.conf['pipe_in_loop']:
            if name in nodes: self.loop_nodes.append(nodes[name])

        inp = self.conf['inp'][0]
        for n in self.loop_nodes:
            if inp in n.mermaid_inps:
                n.mermaid_inps[n.mermaid_inps.index(inp)] = self.name

    def get_mermaid(self, info=None):
        links = []
        inp = self.conf['inp'][0]
        links.append(f'{inp} ==> {self.name}')
        loop_inps = set()
        loop_outs = set()
        for i in self.loop_nodes:
            loop_inps.update(i.mermaid_inps)
            loop_outs.update(i.mermaid_outs)

        l_out = ' & '.join(loop_outs - loop_inps)
        outs = f'{self.name}_done'
        links.append(f'{l_out} ==> {outs}')

        for n in self.next:
            if n.name == 'exit':
                t = f'|total: {info["total_time"]:.2f}s|' if info else ''
                links.append(f'{outs} --o{t} exit')

        defines = [self.__class__.mermaid_shape(i) for i in [self.name, outs]]

        return defines, links

    def get_loop_outs(self):
        outs = []
        for n in self.loop_nodes:
            outs += n.mermaid_outs
        return outs

    async def current_task(self, data, queue, dynamic_tasks):
        inps = await self.get_inps(queue)
        inp = inps[0]
        n = len(inp)
        inp_name = self.conf['inp'][0]

        loop_tasks = []
        loop_data = []
        sub = []
        loop_outs = self.get_loop_outs()
        for item in inp:
            new_data = {}
            loop_data.append(new_data)

            new_queue = collections.defaultdict(asyncio.Queue)
            for k in queue:
                if k == inp_name:
                    new_queue[k].put_nowait(item)
                elif k not in loop_outs:
                    new_queue[k] = queue[k]
            sub.append(new_queue)

            for n in self.loop_nodes:
                task = asyncio.create_task(n.run(new_data, new_queue, loop_tasks))
                loop_tasks.append(task)

        queue['_sub'] = sub

        while not all(t.done() for t in loop_tasks):
            await asyncio.gather(*loop_tasks)

        del queue['_sub']
        for d in loop_data:
            for k, v in d.items():
                if k in data: data[k].append(v)
                else: data[k] = [v]
        for k in loop_data[0]: queue[k].put_nowait(data[k])

    def current_mp_task(self, inps, data, queue, config=None):
        N = len(inps[0])
        loop_outs = self.get_loop_outs()
        for k in loop_outs: data[k] = [DataState.VOID] * N
        for i in range(N):
            new_config = {} if config is None else copy.deepcopy(config)
            if 'loop_index' not in new_config: new_config['loop_index'] = {}
            new_config['loop_index'] |= {k:i for k in self.conf['inp']+loop_outs}
            for node in self.loop_nodes: queue.put((node.name, new_config))

        for node in self.next: queue.put((node.name, config))

class LoopEndNode(Node):
    def current_mp_task(self, data, queue):
        if (inps := self.get_inps_mp(data)):
            inp = inps[0]

            if (node := self.next.get(cond, None)): queue.put(node.name)
            log.debug(f'[BranchNode] condition: {cond}, goto node: {node}')

class BranchNode(Node):
    mermaid_style = 'fill:#445760,color:white'
    mermaid_shape = lambda x: f'{x}{{"{x}"}}'

    def post_init(self):
        if self.conf['use_llm']:
            tree = self.tree
            self.conf['prompt'] = tree.prompt_manager.prompts['branch_node_prompt']
            self.conf['return_json'] = False
            if tree.is_async:
                pipe = LLMPipe(self.name, llm=tree.llm_backend, **self.conf)
            else:
                pipe = LLMPipe(
                        self.name,
                        llm=tree.llm_backend,
                        lock=tree.mp_lock,
                        run_time=tree.mp_manager.list(),
                        inout_log=tree.mp_manager.list(),
                        **self.conf
                        )
            tree.pipe_manager[self.name] = pipe
            self.pipe = pipe

    def update(self, nodes):
        self.next = {}
        for cond, name in self.conf['next'].items():
            if name in nodes: self.next[cond] = nodes[name]

    def get_mermaid(self, info=None):
        inps = ' & '.join(self.mermaid_inps)

        defines = [self.__class__.mermaid_shape(self.name)] + [Data.mermaid_shape(d) for d in self.mermaid_data]

        t = info["detail"][self.name]["avg_time"] if info else None
        t = f'|{t:.2f}s|' if t is not None else ''
        inout_link = f'{inps} ==>{t} {self.name}'

        links = [inout_link]
        for cond, n in self.next.items():
            if n.name == 'exit':
                t = f'|{cond}, total: {info["total_time"]:.2f}s|' if info else f'|{cond}|'
                links.append(f'{self.name} --o{t} exit')
            else:
                links.append(f'{self.name} --o|{cond}| {n.name}')

        return defines, links

    async def add_task(self, data, queue, dynamic_tasks):
        inps = await self.get_inps(queue)
        if self.conf['use_llm']:
            items = list(self.conf['next'].keys())
            cond = await self.pipe(*inps, items)
        else:
            cond = inps[0]

        if (node := self.next.get(cond, None)):
            task = asyncio.create_task(node.run(data, queue, dynamic_tasks), name=node.name)
            dynamic_tasks.append(task)

        log.debug(f'[BranchNode] condition: {cond}, goto node: {node}')

    def current_mp_task(self, inps, data, queue, config=None):
        if self.conf['use_llm']:
            items = list(self.conf['next'].keys())
            cond = self.pipe(*inps, items)
        else:
            cond = inps[0]

        if (node := self.next.get(cond, None)): queue.put((node.name, config))
        log.debug(f'[BranchNode] condition: {cond}, goto node: {node}')

    def export_as_comfyui(self):
        inps = {
            "text": ["TEXT"],
            "use_llm": ["BOOLEAN", {"default": self.conf.get('use_llm', False)}],
        }
        opt_inps = {}
        outs = list(self.conf['next'].keys())
        d = {
            "input": {
                "required": inps,
                "optional": opt_inps
            },
            "input_order": {"required": list(inps.keys())},
            "output": ["TEXT"] * len(outs),
            "output_is_list": [False] * len(outs),
            "output_name": outs,
            "name": self.name,
            "display_name": self.name,
            "description": f"{self.name} 分支流程",
            "python_module": "nodes",
            "category": "控制流",
            "output_node": False,
        }
        return {self.name: d}

    def __str__(self):
        arr = [f'{cond} -> {n.name}' for cond, n in self.next.items()]
        return f"<{self.__class__.__name__}: {self.name}, next: {arr}>"

class ExitNode(Node):
    mermaid_style = 'fill:#3D3E3F,color:white'
    mermaid_shape = lambda x: f'{x}[["{x}"]]'

    def get_mermaid(self, info=None):
        defines = [self.__class__.mermaid_shape(self.name)]
        return defines, []

    async def current_task(self, data, queue, dynamic_tasks):
        if self.conf:
            while not all(t.done() for t in dynamic_tasks if t.get_name() != 'exit'):
                await asyncio.sleep(0.1)

            self.reformat(data)

    def reformat(self, data):
        if self.conf and 'error_msg' not in data:
            ret = {}
            for k, v in self.conf.items():
                if type(v) is str:
                    d = data
                    for i in v.split('.'):
                        if i in d: d = d[i]
                        else: break
                    else:
                        ret[k] = d
                elif type(v) is list and type(v[0]) is dict:
                    d = []
                    for i in range(len(data[list(v[0].values())[0]])):
                        t = {}
                        for m, n in v[0].items():
                            if n in data:
                                t[m] = data[n][i]
                        if t: d.append(t)
                    if d: ret[k] = d

            for k in list(data.keys()): del data[k]
            for k in ret: data[k] = ret[k]

class PipeTree:
    def __init__(self, llm_backend, rag_backend, prompt_manager, name=None, pipeconf:dict=None, pipefile=None, is_async=False):
        self.name = name
        self.pipeconf = pipeconf
        self.pipefile = pipefile
        self.llm_backend = llm_backend
        self.rag_backend = rag_backend
        self.is_async = is_async
        self.perf = []
        if pipeconf is None and pipefile is not None: self.load(pipefile)

        self.start_nodes = []
        self.exit_node = None
        self.prompt_manager = prompt_manager
        self.pipe_manager = {}
        self.node_manager = {}
        self.node_type = collections.defaultdict(set)
        if not is_async:
            self.mp_manager = mp.Manager()
            self.mp_lock = self.mp_manager.Lock()

        self._init()
        self._check()

    def load(self, pipefile):
        if type(pipefile) is str: pipefile = Path(pipefile)
        m = importlib.import_module(str(pipefile).replace('/','.')[:-3])
        self.pipeconf = m.pipe
        if self.name is None: self.name = pipefile.stem

    def _check(self):
        node_names = set(self.node_manager.keys())
        data = set()
        for n in self.node_manager.values(): data.update(n.mermaid_data)
        if (conflict_names := node_names & data):
            log.error(f'conflict between the pipe name and the data name, which will cause errors when drawing mermaid flowchart: {conflict_names}')
            exit()

    def _find_start_nodes(self):
        conf = self.pipeconf
        deps = set()
        for p in conf:
            if (nt := conf[p].get('next', None)):
                if type(nt) is dict:
                    deps.update(list(nt.values()))
                elif type(nt) is list:
                    deps.update(nt)
            deps.update(conf[p].get('pipe_in_loop', []))

        self.start_nodes = [self.node_manager[i] for i in list(set(conf.keys()) - deps)]

    def _init(self):
        if 'exit' not in self.pipeconf: self.pipeconf['exit'] = {}
        for name, conf in self.pipeconf.items():
            if name == 'exit':
                self.exit_node = node = ExitNode(name, conf, self)
            elif 'prompt' in conf:
                node = LLMNode(name, conf, self)
            elif 'rag_param' in conf:
                node = RAGNode(name, conf, self)
            elif 'pipe_in_loop' in conf:
                node = LoopNode(name, conf, self)
            elif 'use_llm' in conf or type(conf.get('next', None)) is dict:
                node = BranchNode(name, conf, self)
            else:
                log.error(f"Unable to identify node type: [{name}] {conf}")
                exit()
            self.node_manager[name] = node

        for n in self.node_manager.values():
            n.update(self.node_manager)
            self.node_type[n.__class__].add(n.name)
            if type(n) is LoopNode: self.node_type[n.__class__].add(f'{n.name}_done')
            self.node_type[Data].update(n.mermaid_data)

        self._find_start_nodes()
        if not self.start_nodes:
            log.error(f"Can't find start entry in pipes.")
            exit()
        log.debug(f"'{self.name}' tree initialization successful, start nodes: {self.start_nodes}")

    def export_conf(self):
        conf = copy.deepcopy(self.pipeconf)
        for pipe_conf in conf.values():
            if 'format' in pipe_conf:
                for k, v in pipe_conf['format'].items():
                    pipe_conf['format'][k] = str(v)
        return conf

    def reset(self):
        self.perf = []
        for node in self.node_manager.values(): node.reset()

    def tree2mermaid(self, info=None):
        mermaid = 'graph TD\n'
        indent = ' '*4
        defines = set()
        links = set()
        passed_nodes = set()
        nodes = self.start_nodes[:]
        while nodes:
            n = nodes.pop(0)
            passed_nodes.add(n)
            defs, lks = n.get_mermaid(info)
            defines.update(defs)
            links.update(lks)
            for i in n.loop_nodes + (n.next if type(n.next) is list else list(n.next.values())):
                if i not in passed_nodes: nodes.append(i)

        for i in list(defines)+list(links):
            mermaid += f'{indent}{i}\n'

        # add style
        for c, items in self.node_type.items():
            name = c.__name__.upper()
            mermaid += f'{indent}classDef {name} {c.mermaid_style}\n'
            mermaid += f'{indent}class {",".join(items)} {name}\n'

        return mermaid

    def perf2mermaid(self):
        mermaid = 'gantt\ntitle Task Timeline\ndateFormat  x\naxisFormat  %M:%S.%L\n'
        base_time = self.perf[0][2]
        data = collections.defaultdict(list)
        loop_end = {}
        for name, e, start_time, end_time in self.perf:
            if 'pid' in name:
                arr = name.split(': ')
                n = f'{arr[0]}_{int(arr[1]):0>2d}'
            else:
                n = name
            s = (start_time - base_time) * 1000
            Δ = (end_time - start_time) * 1000
            data[n].append((e, s, Δ))
            # if e in pipe:
            #     if pipe[e]['mode'] == 'loop':
            #         loop_end[f'{e}_end'] = (n, e, s)
            #     else:
            #         data[n].append((e, s, Δ))
            # elif e in loop_end:
            #     n, e, s_ = loop_end[e]
            #     Δ_ = s + Δ - s_
            #     data[n].append((e, s_, Δ_))
        
        for k in sorted(data.keys()):
            mermaid += f'section {k}\n'
            for e, s, Δ in data[k]:
                # if pipe[e]['mode'] == 'loop':
                #     mermaid += f'{e}: done, {s:.0f}, {Δ:.0f}ms\n'
                # else:
                mermaid += f'{e}: {s:.0f}, {Δ:.0f}ms\n'

        return mermaid

    async def async_run(self, inp_data):
        self.reset()
        data = copy.deepcopy(inp_data)
        dynamic_tasks = []
        queue = collections.defaultdict(asyncio.Queue)
        for k, v in data.items(): queue[k].put_nowait(v)
        await asyncio.gather(*[asyncio.create_task(n.run(data, queue, dynamic_tasks)) for n in self.start_nodes])
        while not all(t.done() for t in dynamic_tasks):
            await asyncio.gather(*dynamic_tasks)
        return data

    def task_process(self, pid, task_queue, perf_queue, pipe_manager, data, lock):
        name = f'pid: {pid}'
        log.debug(f'{name}, start')

        print(self.node_manager)

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

    def mp_task(self, pid, data, task_queue, perf_queue):
        name = f'pid: {pid}'
        lock = self.mp_lock
        log.debug(f'{name}, start')

        try:
            while True:
                try:
                    node_name, config = task_queue.get_nowait()
                    if node_name == 'exit':
                        # if task_queue.qsize() == 0:
                        task_queue.put(('exit', None))
                        log.debug(f'{name}, exit')
                        break
                except queue.Empty: continue

                self.node_manager[node_name].run(name, data, task_queue, perf_queue, config)
        except Exception as e:
            error_msg = traceback.format_exc()
            with lock: data['error_msg'] = error_msg
            log.error(f'[{name}]:\n{error_msg}')
            task_queue.put(('exit', {}))
            log.debug(f'{name}, exit')

    def mp_run(self, inp_data, core_num=4):
        self.reset()
        task_queue = self.mp_manager.Queue()
        perf_queue = self.mp_manager.Queue()
        data       = self.mp_manager.dict()
        for n in self.start_nodes: task_queue.put((n.name, None))
        for k, v in inp_data.items(): data[k] = v

        processes = []
        for i in range(core_num):
            p = mp.Process(target=self.mp_task, args=(i, data, task_queue, perf_queue))
            processes.append(p)
            p.start()
        for p in processes: p.join()
        while not perf_queue.empty(): self.perf.append(perf_queue.get())

        data = dict(data)
        self.exit_node.reformat(data)
        return data

    def __str__(self):
        loop_num = sum([type(n) is LoopNode for n in self.node_manager.values()])
        branch_num = sum([type(n) is BranchNode for n in self.node_manager.values()])
        return f"<PipeTree '{self.name}': nodes: {len(self.node_manager)}, loop: {loop_num}, branch: {branch_num}, async: {self.is_async}>"

    def __repr__(self):
        return self.__str__()