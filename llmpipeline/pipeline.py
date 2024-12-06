import os
import time
import json
import uuid
import datetime
from .log import log, log_dir
from .pipetree import PipeTree
from .utils import check_cmd_exist, get_ordered_task

class Pipeline:
    def __init__(self, llm_backend, rag_backend, prompt_manager, pipeconf=None, pipefile=None, is_async=False, is_seq=False):
        self.llm_backend = llm_backend
        self.rag_backend = rag_backend
        self.is_async = is_async
        self.is_seq = is_seq
        self.name = f'pipeline-{datetime.datetime.now().strftime("%m/%d/%Y_%H:%M:%S")}'
        if pipeconf or pipefile:
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
                tmp_file = f'/tmp/{uuid.uuid4()}'
                with open(tmp_file, 'w') as f: f.write(info["mermaid"]["pipe"])
                log.debug(f'Save pipeline png in: {tmp_file}')
                os.popen(f'mmdc -i {tmp_file} -o {pipe_img} -s 3')
                log.debug(f'save {pipe_img}')
                perf_img = str(log_dir / f"{fname}_perf.png")
                os.popen(f'echo "{info["mermaid"]["perf"]}" | mmdc -i - -o {perf_img} -s 3')
                log.debug(f'save {perf_img}')
                # md_pipe = f"![pipe_img]({pipe_img.split('/')[1]})"
                # md_perf = f"![perf_img]({perf_img.split('/')[1]})"
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

    def mp_run(self, data, core_num=4, save_perf=False):
        start_t = time.time()
        result = self.pipetree.mp_run(data, core_num)
        log.debug(f'final out:\n{json.dumps(result, indent=4, ensure_ascii=False)}')
        info = self.gen_info(result, start_t, save_perf)
        return result, info

    async def async_run(self, data, save_perf=False):
        start_t = time.time()
        result = await self.pipetree.async_run(data)
        log.debug(f'final out:\n{json.dumps(result, indent=4, ensure_ascii=False)}')
        info = self.gen_info(result, start_t, save_perf)
        return result, info

    def seq_run(self, prompt_id, ws_id, task_data, send_msg):
        task_order = get_ordered_task(task_data)
        task_out = {}

        for task_id in task_order:
            msg = {
                "node": task_id, 
                "display_node": task_id,
                "prompt_id": prompt_id
            }
            send_msg("executing", msg, ws_id)
            task = task_data[task_id]
            task_type = task['class_type']

            if task_type == 'InputText':
                task_out[task_id] = [task['inputs']['input']]
            elif task_type == 'PreviewText':
                inp_id, inp_idx = task['inputs']['out'][0].split('-')
                inp_idx = int(inp_idx)
                out = task_out[inp_id][inp_idx] if inp_id in task_out else None

                msg = {
                    "node": task_id,
                    "display_node": task_id,
                    "output": {
                        "string": [out],
                    },
                    "prompt_id": prompt_id
                }
                send_msg("executed", msg)
            elif 'prompt' in task['inputs']:
                prompt = task['inputs']['prompt']
                for k, v in task['inputs'].items():
                    if k == 'prompt': continue
                    elif k == '模型' or k == 'model': continue
                    else:
                        inp_id, inp_idx = v[0].split('-')
                        inp_idx = int(inp_idx)
                        inp = task_out[inp_id][inp_idx] if inp_id in task_out else None
                        prompt = prompt.replace(k, inp)
                out = self.llm_backend(prompt)
                task_out[task_id] = [out]

                msg = {
                    "node": task_id,
                    "display_node": task_id,
                    "output": {
                        "string": [out],
                    },
                    "prompt_id": prompt_id
                }
                send_msg("executed", msg)
            elif 'kb' in task['inputs']:
                ...
            elif 'use_llm' in task['inputs']:
                ...
            else:
                time.sleep(3)

        return msg

    def fake_run(self, prompt_id, ws_id, task_data, send_msg):
        # 模拟
        for node_id in [2, 3, 8, 5, 7, 6]:
        # for node_id in [4, 10, 11, 5, 13]:
            data = {
                "node": str(node_id), 
                "display_node": str(node_id),
                "prompt_id": prompt_id
            }
            send_msg("executing", data, ws_id)
            time.sleep(3)

        # for i in range(20):
        #     data = {
        #         "value": i+1,
        #         "max": 20,
        #         "prompt_id": prompt_id,
        #         "node": "13"
        #     }
        #     self.send_msg("progress", data, ws_id)
        #     time.sleep(.5)

        # for node_id in [12, 9]:
        #     data = {
        #         "node": str(node_id), 
        #         "display_node": str(node_id),
        #         "prompt_id": prompt_id
        #     }
        #     self.send_msg("executing", data, ws_id)
        #     time.sleep(1)

        # out = {
        #     "node": "9",
        #     "display_node": "9",
        #     "output": {
        #         "images": [{
        #             "filename": "doubao.png",
        #             "subfolder": "",
        #             "type": "temp"
        #         }],
        #     },
        #     "prompt_id": prompt_id
        # }

        out = {
            "node": "6",
            "display_node": "6",
            "output": {
                "string": ["1234dededexdeee\ndefwefew"],
            },
            "prompt_id": prompt_id
        }
        send_msg("executed", out)
        return out

    @property
    def run(self):
        if self.is_async:
            log.debug(f"Run '{self.name}' pipeline in coroutine")
            return self.async_run
        elif self.is_seq:
            log.debug(f"Run '{self.name}' pipeline in sequential")
            return self.seq_run
        else:
            log.debug(f"Run '{self.name}' pipeline in multiprocess")
            return self.mp_run

