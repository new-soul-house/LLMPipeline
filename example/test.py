import sys 
sys.path.append("..")
from llmpipeline import LLMPipeline, Prompt

# set custom prompt
example_prompt = Prompt("""
...
{inp1}
xxx
""", keys=['{inp1}'])

# set api
def llm_api(inp):
    return inp

def rag_api(inp):
    return inp

# set input data
data = {
    'inp': 'test input text ...',
}

# set pipeline
demo_pipe = {
    'process_input': {
        'mode': 'llm',
        'prompt': example_prompt,
        'return_json': False,
        'inp': ['inp'],
        'out': 'out1',
        'next': ['rag1'],
    },
    'rag1': {
        'mode': 'rag',
        'inp': ['out1'],
        'out': 'out2',
        'next': ['exit'],
    },
}

# running pipeline
pipeline = LLMPipeline(demo_pipe, data, llm_api, rag_api)
result, info = pipeline.run('process_input', core_num=2, save_pref=True)

