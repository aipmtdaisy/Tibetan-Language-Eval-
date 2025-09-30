import os
import yaml
from dataclasses import dataclass
from typing import Dict, Any, Optional, List

@dataclass
class PromptConfig:
    max_shots: int
    system_message: str
    user_template: str
    few_shot_template: str
    temperature: Optional[float] = None
    top_p: Optional[float] = None

@dataclass
class ModelConfig:
    url: str
    model_name: str
    api_key: str
    prompt_config: PromptConfig
    stream: Optional[bool] = False

    def get_request_params(self, question: str, few_shot_examples: str = "") -> dict:
        """构建请求参数"""
        messages = []

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

        # For Anthropic Claude API, system message goes as a separate parameter
        if self.prompt_config.system_message and "anthropic" in self.url.lower():
            params["system"] = self.prompt_config.system_message
            params["max_tokens"] = 1024  # Required for Claude API
        # For other APIs, add system message to messages array
        elif self.prompt_config.system_message:
            messages.insert(0, {
                "role": "system",
                "content": self.prompt_config.system_message
            })

        # 添加可选参数
        if self.prompt_config.temperature is not None:
            params["temperature"] = self.prompt_config.temperature
        if self.prompt_config.top_p is not None:
            params["top_p"] = self.prompt_config.top_p

        return params

@dataclass
class ProcessConfig:
    input_folder: str
    output_folder_template: str
    few_shot_folder: str
    batch_size: int = 32
    max_retries: int = 10
    timeout: int = 60
    retry_wait_time: int = 2

@dataclass
class EvaluationMethodConfig:
    enabled: bool
    metrics_file_template: str
    filtered_file_prefix: str

@dataclass
class EvaluationConfig:
    output_folder_template: str
    methods: Dict[str, EvaluationMethodConfig]
    general_category_folder: str
    exclude_list: List[str]

def load_config(config_file: str = "config.yaml") -> tuple[Dict[str, ModelConfig], PromptConfig, ProcessConfig, EvaluationConfig]:
    """加载YAML配置文件
    
    Args:
        config_file: YAML配置文件路径，默认为当前目录下的config.yaml
        
    Returns:
        tuple: (模型配置字典, 提示词配置, 处理配置, 评估配置)
    """
    # 获取配置文件的绝对路径
    if not os.path.isabs(config_file):
        config_file = os.path.join(os.path.dirname(__file__), config_file)
    
    # 读取YAML文件
    with open(config_file, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    # 加载提示词配置
    prompt_config = PromptConfig(**config['prompt_config'])
    
    # 加载处理配置
    process_config = ProcessConfig(**config['process_config'])
    
    # 加载评估配置
    eval_methods = {}
    for method_name, method_config in config['evaluation_config']['methods'].items():
        eval_methods[method_name] = EvaluationMethodConfig(**method_config)
    
    evaluation_config = EvaluationConfig(
        output_folder_template=config['evaluation_config']['output_folder_template'],
        methods=eval_methods,
        general_category_folder=config['evaluation_config']['general_category_folder'],
        exclude_list=config['evaluation_config']['exclude_list']
    )
    
    # 加载所有模型配置
    model_configs = {}
    for model_id, model_data in config['model_configs'].items():
        # 为每个模型创建一个独立的PromptConfig实例
        model_prompt_config = PromptConfig(
            max_shots=prompt_config.max_shots,
            system_message=prompt_config.system_message,
            user_template=prompt_config.user_template,
            few_shot_template=prompt_config.few_shot_template,
            temperature=model_data.get('temperature'),
            top_p=model_data.get('top_p')
        )
        
        # 创建ModelConfig实例
        model_configs[model_id] = ModelConfig(
            url=model_data['url'],
            model_name=model_data['name'],
            api_key=model_data['api_key'],
            prompt_config=model_prompt_config,
            stream=model_data.get('stream', False)
        )
    
    return model_configs, prompt_config, process_config, evaluation_config