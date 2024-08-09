from llmpipeline import LLMPipeline, Prompt

# set custom prompt
example_prompt = Prompt("""
...
{inp1}
xxx
""", keys=['{inp1}'])

# set api
def llm_api(inp):
    ...
    return out

def rag_api(inp):
    ...
    return out

# set input data
data = {
    'inp': 'test input text ...',
}

# set pipeline
demo_pipe = {
    'process_input': {
        'prompt': example_prompt,
        'format': {'out1': list, 'out2': str}, # check return json format
        'inp': ['inp'],
        'out': ['out1', 'out2'],
        'next': ['rag1', 'loop_A'], # specify the next pipeline
    },
    'rag1': {
        'rag_backend': rag_api2, # specific api can be set for the current pipe via 'rag_backend' or 'llm_backend'.
        'inp': ['out2'],
        'out': 'out8',
    },
    'loop_A': { # here is iterating over a list 'out1'
        'inp': 'out1',
        'pipe_in_loop': ['rag2', 'llm_process', 'rag3', 'rag4', 'llm_process2', 'llm_process3'],
        'next': ['exit'], # 'exit' is specific pipe mean to end
    },
    'rag2': {
        'inp': ['out1'],
        'out': 'out3',
    },
    'llm_process2': {
        'prompt': llm_process2_prompt,
        'format': {'xxx': str, "xxx": str},
        'inp': ['inp', 'out4', 'out8'],
        'out': 'final_out1',
    },
    ...
}

# running pipeline
pipeline = LLMPipeline(demo_pipe, llm_api, rag_api)
result, info = pipeline.run(data, core_num=4, save_pref=True)
