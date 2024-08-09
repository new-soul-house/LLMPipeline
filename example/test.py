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
        'prompt': example_prompt,
        'return_json': False,
        'inp': ['inp'],
        'out': 'out1',
        'next': ['rag1'],
    },
    'rag1': {
        'inp': ['out1'],
        'out': 'out2',
        'next': ['exit'],
    },
}

# running pipeline
pipeline = LLMPipeline(demo_pipe, llm_api, rag_api)
result, info = pipeline.run(data, core_num=2, save_pref=True)

