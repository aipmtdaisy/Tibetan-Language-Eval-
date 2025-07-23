from dataclasses import dataclass, field
from typing import Optional

@dataclass
class PromptConfig:
    max_shots: int = 0
    temperature: Optional[float] = None
    top_p: Optional[float] = None
    system_message: str = ""
    user_template: str = "གཤམ་གསལ་འདི་འདེམས་ཀ་གཅིག་མའི་དྲི་བ་ཡིན་པས། ལན་འདེམས་ཀ་ཡང་དག་པ་དེ་ཐད་ཀར་སྟོན་རོགས། ལན་འདེམས་ཀ་ A B C D བཞིའི་ནང་ནས་གཅིག་འདེམས་རོགས།\n\n{few_shot_examples}དྲི་བ།\n{question}\nལན་ནི།"
    few_shot_template: str = "དྲི་བ།\n{question}\nལན་ནི། {answer}\n\n"

@dataclass
class ModelConfig:
    url: str
    model_name: str
    api_key: str
    prompt_config: PromptConfig
    stream: Optional[bool] = False  # 添加流式输出配置

    def get_request_params(self, question: str, few_shot_examples: str = "") -> dict:
        """构建请求参数"""
        messages = []
        
        # 添加系统消息（如果有）
        if self.prompt_config.system_message:
            messages.append({
                "role": "system",
                "content": self.prompt_config.system_message
            })
        
        # 构建用户消息（包含few-shot示例，如果有的话）
        user_content = self.prompt_config.user_template.format(
            few_shot_examples=few_shot_examples,
            question=question
        )
        messages.append({
            "role": "user",
            "content": user_content
        })

        # 构建请求参数
        params = {
            "model": self.model_name,
            "messages": messages,
        }

        # 添加可选参数
        if self.prompt_config.temperature is not None:
            params["temperature"] = self.prompt_config.temperature
        if self.prompt_config.top_p is not None:
            params["top_p"] = self.prompt_config.top_p

        return params

@dataclass
class ProcessConfig:
    input_folder: str
    output_folder: str
    few_shot_folder: str
    batch_size: int = 32
    max_retries: int = 10
    timeout: int = 60
    retry_wait_time: int = 2