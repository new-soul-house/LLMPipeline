import os
import time
import json
import datetime
from .log import log, log_dir
from .pipetree import PipeTree
from .utils import check_cmd_exist

class Pipeline:
    def __init__(self, llm_backend, rag_backend, prompt_manager, pipeconf:dict=None, pipefile=None, is_async=False):
        self.is_async = is_async
        self.pipetree = PipeTree(llm_backend, rag_backend, prompt_manager, pipeconf=pipeconf, pipefile=pipefile, is_async=is_async)
        self.name = self.pipetree.name

    def gen_info(self, data, start_t, save_perf=False):
        pipe_manager = self.pipetree.pipe_manager

        info = {
            'perf': self.pipetree.perf,
            'exec_path': [n[1] for n in self.pipetree.perf],
            'detail': {},
            'total_time': time.time()-start_t,
            'mermaid': {},
        }
        for k in sorted(pipe_manager, key=lambda k: pipe_manager[k].time or -1):
            info['detail'][k] = {
                # 'run_time': list(pipe_manager[k].run_time),
                'avg_time': pipe_manager[k].time,
            }

        if save_perf and 'error_msg' not in data:
            info['mermaid']['pipe'] = self.pipetree.tree2mermaid(info)
            info['mermaid']['perf'] = self.pipetree.perf2mermaid()
            fname = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
            if check_cmd_exist('mmdc'):
                pipe_img = str(log_dir / f'{fname}_pipe.png')
                os.popen(f'echo "{info["mermaid"]["pipe"]}" | mmdc -o {pipe_img}')
                log.debug(f'save {pipe_img}')
                perf_img = str(log_dir / f"{fname}_perf.png")
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

    def mp_run(self, data, core_num=4, save_pref=False):
        start_t = time.time()
        result = self.pipetree.mp_run(data, core_num)
        log.debug(f'final out:\n{json.dumps(result, indent=4, ensure_ascii=False)}')
        info = self.gen_info(result, start_t, save_pref)
        return result, info

    async def async_run(self, data, save_perf=False):
        start_t = time.time()
        result = await self.pipetree.async_run(data)
        log.debug(f'final out:\n{json.dumps(result, indent=4, ensure_ascii=False)}')
        info = self.gen_info(result, start_t, save_perf)
        return result, info

    @property
    def run(self):
        if self.is_async:
            log.debug(f"Run '{self.name}' pipeline in coroutine")
            return self.async_run
        else:
            log.debug(f"Run '{self.name}' pipeline in multiprocess")
            return self.mp_run

