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
    "claude-sonnet-4-5": {
        "name": "claude-sonnet-4-5-20250929",
        "url": "https://api.anthropic.com/v1/messages",
        "temperature": 1.0,
        "api_key": "your-claude-api-key",
        "model_id": "claude-sonnet-4-5"
    },
    "claude-opus-4-1": {
        "name": "claude-opus-4-1-20250805",
        "url": "https://api.anthropic.com/v1/messages",
        "temperature": 1.0,
        "api_key": "your-claude-api-key",
        "model_id": "claude-opus-4-1"
    },
    # "claude-opus-4": {
    #     "name": "claude-opus-4-20250514",
    #     "url": "https://api.anthropic.com/v1/messages",
    #     "temperature": 1.0,
    #     "api_key": "your-claude-api-key",
    #     "model_id": "claude-opus-4"
    # },
    # "claude-sonnet-4": {
    #     "name": "claude-sonnet-4-20250514",
    #     "url": "https://api.anthropic.com/v1/messages",
    #     "temperature": 1.0,
    #     "api_key": "your-claude-api-key",
    #     "model_id": "claude-sonnet-4"
    # },
    # "claude-3-7-sonnet": {
    #     "name": "claude-3-7-sonnet-20250219",
    #     "url": "https://api.anthropic.com/v1/messages",
    #     "temperature": 1.0,
    #     "api_key": "your-claude-api-key",
    #     "model_id": "claude-3-7-sonnet"
    # },
    # "claude-3-5-haiku": {
    #     "name": "claude-3-5-haiku-20241022",
    #     "url": "https://api.anthropic.com/v1/messages",
    #     "temperature": 1.0,
    #     "api_key": "your-claude-api-key",
    #     "model_id": "claude-3-5-haiku"
    # },
    # "claude-3-haiku": {
    #     "name": "claude-3-haiku-20240307",
    #     "url": "https://api.anthropic.com/v1/messages",
    #     "temperature": 1.0,
    #     "api_key": "your-claude-api-key",
    #     "model_id": "claude-3-haiku"
    # },
    "gemini-2-5-pro": {
        "name": "gemini-2.5-pro",
        "url": "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-pro:generateContent",
        "temperature": 1.0,
        "top_p": 0.95,
        "api_key": "your-gemini-api-key",
        "model_id": "gemini-2-5-pro"
    },
    "gemini-2-5-flash": {
        "name": "gemini-2.5-flash",
        "url": "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent",
        "temperature": 1.0,
        "top_p": 0.95,
        "api_key": "your-gemini-api-key",
        "model_id": "gemini-2-5-flash"
    }
}