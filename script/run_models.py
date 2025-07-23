import sys
import os
import subprocess
from config_loader import load_config, ModelConfig
from logger import LoggerManager
from model_processor import ModelProcessor
from typing import Dict, Any

def get_model_config(model_configs: Dict[str, Any], prompt_config: Any, model_type: str) -> tuple[ModelConfig, str]:
    """获取模型配置
    Args:
        model_configs: 所有模型的配置字典
        prompt_config: 提示词配置
        model_type: 模型类型，如 'claude', 'gemini', 'gpt4' 等
    Returns:
        ModelConfig: 模型配置
        str: 模型ID（用于文件夹命名）
    """
    if model_type not in model_configs:
        raise ValueError(f'不支持的模型类型: {model_type}')
        
    model_config = model_configs[model_type]
    # 设置提示词配置
    model_config.prompt_config = prompt_config
    return model_config, model_type

def run_model(model_configs: Dict[str, Any], prompt_config: Any, process_config: Any, model_type: str, process_params: Dict[str, Any] = None):
    """运行指定类型的模型
    Args:
        model_configs: 所有模型的配置字典
        prompt_config: 提示词配置
        process_config: 处理配置
        model_type: 模型类型，如 'claude', 'gemini', 'gpt4' 等
        process_params: 处理参数，如果为None则使用默认配置
    """
    # 获取模型配置
    model_config, model_id = get_model_config(model_configs, prompt_config, model_type)
    
    # 设置输出文件夹
    process_config.output_folder = process_config.output_folder_template.format(model_id=model_id)
    
    # 更新处理参数（如果有）
    if process_params:
        for key, value in process_params.items():
            setattr(process_config, key, value)
    
    # 初始化日志
    logger_manager = LoggerManager(f"{model_id}_processor")
    
    # 创建处理器并执行
    processor = ModelProcessor(model_config, process_config, logger_manager)
    processor.process_all_files()
    
    # 运行评估脚本
    try:
        script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "auto_evaluate.py")
        subprocess.run([sys.executable, script_path, model_id], check=True)
        print(f"评估完成：{model_id}")
    except subprocess.CalledProcessError as e:
        print(f"评估脚本执行失败：{str(e)}")
    except Exception as e:
        print(f"运行评估脚本时出错：{str(e)}")

def main():
    # 加载所有配置
    model_configs, prompt_config, process_config, _ = load_config()
    
    # 运行多个模型
    models = list(model_configs.keys())
    for model_type in models:
        print(f'\n开始运行 {model_type} 模型...')
        run_model(model_configs, prompt_config, process_config, model_type)
        print(f'{model_type} 模型运行完成')

if __name__ == "__main__":
    main()