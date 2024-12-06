from . import *

def llm_client(is_async=False):
    if is_async:
        return async_completion
    else:
        return completion

def completion(text):
    payload = json.dumps({
        "action": "To user",
        "parent_messages": [
            {
                "action": "From user",
                "content": text
            }
        ],
        "gen_kwargs": {
            "model": config.pulse_model,
            "num_return_sequences": 1,
            "max_new_token":4096
        }
    })
    headers = {
        'accept': 'application/json',
        'Authorization': f'Bearer {config.pulse_token}',
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", config.pulse_url, headers=headers, data=payload, verify=False)
    if response.status_code != 200:
        raise Exception(f"Failed to generate completion: {response.text}")

    return response.json()['messages'][0]['content']['parts'][0]

async def async_completion(text):
    messages = [
        {
            'action': 'From user', # 'To user'
            'content': text,
        }
    ]

    async with llm_sem:
        input_data = {
            "action": "To user",
            "parent_messages": messages,
            "gen_kwargs": {
                "model": config.pulse_model,
                "num_return_sequences": 1,
                "temperature": config.llm.temperature,
                "top_p": config.llm.top_p,
                "top_k": config.llm.top_k,
                "max_tokens": config.llm.max_tokens,
                "repetition_penalty": config.llm.repetition_penalty,
            }
        }

        return await _get_completion(
            input_data=input_data,
            retry=config.llm.retry_count
        )

async def _get_completion(input_data: dict, retry: int = 5):
    try:
        async with httpx.AsyncClient(verify=False) as client:
            async with client.stream(
                "POST",
                config.pulse_url,
                json=input_data,
                headers={
                    "Authorization": f"Bearer {config.pulse_token}",
                },
                timeout=600,
            ) as stream:
                # error
                if stream.status_code != 200:
                    error_detail = ""
                    try:
                        error_detail = (await stream.aread()).decode("utf8")
                        error_detail = str(json.loads(error_detail))
                    except:
                        pass

                    raise HTTPException(status_code=500, detail=error_detail)

                content = (await stream.aread()).decode("utf8")
                content = json.loads(content)
                content = "".join(content['messages'][0]['content']['parts'])
                return content
    except Exception as e:
        # logger.error(json.dumps({
        #     "retry": retry,
        #     "input": input_data,
        #     "error": traceback.format_exc()
        # }, ensure_ascii=False, indent=4))
        # 重试次数到达极限
        if retry == 0: raise e

        return await _get_completion(
            input_data=input_data,
            retry=retry-1,
        )
