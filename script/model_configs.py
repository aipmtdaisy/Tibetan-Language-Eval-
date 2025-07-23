# 提示词配置
PROMPT_CONFIG = {
    "max_shots": 5,
    "system_message": "",
    "user_template": "གཤམ་གསལ་འདི་འདེམས་ཀ་གཅིག་མའི་དྲི་བ་ཡིན་པས། ལན་འདེམས་ཀ་ཡང་དག་པ་དེ་ཐད་ཀར་སྟོན་རོགས། ལན་འདེམས་ཀ་ A B C D བཞིའི་ནང་ནས་གཅིག་འདེམས་རོགས།\n\n{few_shot_examples}དྲི་བ།\n{question}\nལན་ནི།",
    "few_shot_template": "དྲི་བ།\n{question}\nལན་ནི། {answer}\n\n"
}

# 处理配置
PROCESS_CONFIG = {
    "input_folder": "../Question_Answer",
    "output_folder_template": "../model_answer/{model_id}",  # 输出文件夹模板，会自动替换{model_id}
    "few_shot_folder": "../5_shot_Question_Answer",
    "batch_size": 32,
    "max_retries": 10,
    "timeout": 60,
    "retry_wait_time": 2
}

# 模型配置
MODEL_CONFIGS = {
    "claude": {
        "name": "claude-3-5-sonnet-20241022",
        "url": "https://api.openai99.top/v1/chat/completions",
        "temperature": 1.0,
        "api_key": "your-claude-api-key",
        "model_id": "claude"
    },
    "deepseekr1": {
        "name": "deepseek-r1",
        "url": "https://api.openai99.top/v1/chat/completions",
        "temperature": 1.0,
        "stream": True,
        "api_key": "your-api-key",
        "model_id": "deepseekr1"
    },
    "deepseekv3": {
        "name": "deepseek-v3",
        "url": "https://api.openai99.top/v1/chat/completions",
        "temperature": 1.0,
        "api_key": "your-api-key",
        "model_id": "deepseekv3"
    },
    "gemini": {
        "name": "gemini-1.5-flash",
        "url": "https://api.openai99.top/v1/chat/completions",
        "top_p": 0.95,
        "api_key": "your-gemini-api-key",
        "model_id": "gemini"
    },
    "gpt3.5turbo": {
        "name": "gpt-3.5-turbo",
        "url": "https://api.openai99.top/v1/chat/completions",
        "temperature": 1.0,
        "top_p": 1.0,
        "api_key": "your-openai-api-key",
        "model_id": "gpt3.5turbo"
    },
    "gpt4o": {
        "name": "gpt-4o",
        "url": "https://api.openai99.top/v1/chat/completions",
        "temperature": 1.0,
        "top_p": 1.0,
        "api_key": "your-openai-api-key",
        "model_id": "gpt4o"
    },
    "llama3.18b": {
        "name": "llama-3.1-8b",
        "url": "https://api.openai99.top/v1/chat/completions",
        "temperature": 0.6,
        "top_p": 0.9,
        "api_key": "your-api-key",
        "model_id": "llama3.18b"
    },
    "llama3.170b": {
        "name": "llama-3.1-70b",
        "url": "https://api.openai99.top/v1/chat/completions",
        "temperature": 0.6,
        "top_p": 0.9,
        "api_key": "your-api-key",
        "model_id": "llama3.170b"
    },
    "llama3.1405b": {
        "name": "llama-3.1-405b",
        "url": "https://api.openai99.top/v1/chat/completions",
        "temperature": 0.6,
        "top_p": 0.9,
        "api_key": "your-api-key",
        "model_id": "llama3.1405b"
    },
    "o1mini": {
        "name": "o1-mini",
        "url": "https://api.openai99.top/v1/chat/completions",
        "temperature": 1.0,
        "top_p": 1.0,
        "stream": True,
        "api_key": "your-api-key",
        "model_id": "o1mini"
    },
    "qwen2.57b": {
        "name": "qwen2.5-7b-instruct",
        "url": "https://api.openai99.top/v1/chat/completions",
        "temperature": 0.7,
        "top_p": 0.8,
        "api_key": "your-api-key",
        "model_id": "qwen2.57b"
    },
    "qwen2.532b": {
        "name": "qwen2.5-32b-instruct",
        "url": "https://api.openai99.top/v1/chat/completions",
        "temperature": 0.7,
        "top_p": 0.8,
        "api_key": "your-api-key",
        "model_id": "qwen2.532b"
    },
    "qwen2.572b": {
        "name": "qwen2.5-72b-instruct",
        "url": "https://api.openai99.top/v1/chat/completions",
        "temperature": 0.7,
        "top_p": 0.8,
        "api_key": "your-api-key",
        "model_id": "qwen2.572b"
    }
}