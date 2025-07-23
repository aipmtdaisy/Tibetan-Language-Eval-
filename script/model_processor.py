import json
import os
import requests
import random
import concurrent.futures
from tqdm import tqdm
import time
from typing import List, Dict, Any, Optional  # 添加 Optional 导入
from config import ModelConfig, ProcessConfig  # 添加 ProcessConfig 导入
from logger import LoggerManager

class ModelProcessor:
    def __init__(
        self,
        model_config: ModelConfig,
        process_config: ProcessConfig,
        logger_manager: LoggerManager
    ):
        self.model_config = model_config
        self.process_config = process_config
        self.logger = logger_manager.get_logger()
        self.few_shot_examples = {}
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    def load_few_shot_examples(self, file_name: str) -> List[Dict]:
        """加载few-shot示例"""
        if file_name in self.few_shot_examples:
            return self.few_shot_examples[file_name]
    
        few_shot_file = os.path.join(
            os.path.dirname(self.process_config.few_shot_folder),
            os.path.basename(self.process_config.few_shot_folder),
            file_name
        )
        
        # 如果设置了 max_shots 但找不到文件，则报错
        if self.model_config.prompt_config.max_shots > 0 and not os.path.exists(few_shot_file):
            error_msg = f"已设置 max_shots={self.model_config.prompt_config.max_shots}，但找不到 few-shot 文件: {few_shot_file}"
            self.logger.error(error_msg)
            raise FileNotFoundError(error_msg)
    
        try:
            with open(few_shot_file, 'r', encoding='utf-8') as f:
                examples = [json.loads(line.strip()) for line in f if line.strip()]
                
            # 验证示例格式
            valid_examples = []
            for example in examples:
                if all(key in example for key in ["loc", "polished_ti_content", "answer"]):
                    valid_examples.append(example)
                else:
                    self.logger.warning(f"无效的few-shot示例格式: {example}")
            
            if not valid_examples and self.model_config.prompt_config.max_shots > 0:
                error_msg = f"已设置 max_shots={self.model_config.prompt_config.max_shots}，但没有有效的 few-shot 示例"
                self.logger.error(error_msg)
                raise ValueError(error_msg)
                
            self.few_shot_examples[file_name] = valid_examples
            return valid_examples
        except Exception as e:
            if self.model_config.prompt_config.max_shots > 0:
                raise  # 如果设置了 max_shots，则向上传递异常
            self.logger.error(f"加载few-shot示例失败: {str(e)}")
            return []

    def get_few_shot_examples(self, file_name: str, num_shots: int) -> str:
        """获取few-shot示例文本"""
        examples = self.load_few_shot_examples(file_name)
        if not examples:
            return ""

        # 随机选择指定数量的示例
        selected = random.sample(
            examples, 
            min(num_shots, len(examples), self.model_config.prompt_config.max_shots)
        )
        
        # 构建few-shot文本
        few_shot_text = ""
        for example in selected:
            few_shot_text += self.model_config.prompt_config.few_shot_template.format(
                question=example["polished_ti_content"],
                answer=example["answer"]
            )
        return few_shot_text

    def make_request(self, payload: Dict[str, Any], index: Optional[int] = None) -> Dict[str, Any]:
        """统一的请求处理方法
        Args:
            payload: 请求参数
            index: 请求的索引号，用于日志和流式输出显示，可选
        Returns:
            Dict: API响应结果
        """
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.model_config.api_key}"
        }
        
        for attempt in range(self.process_config.max_retries):
            try:
                response = requests.post(
                    self.model_config.url,
                    headers=headers,
                    json=payload,
                    timeout=self.process_config.timeout,
                    stream=self.model_config.stream
                )
                
                if response.status_code == 200:
                    if self.model_config.stream:
                        # 处理流式响应
                        full_response = ""
                        try:
                            for line in response.iter_lines():
                                if not line:
                                    continue
                                    
                                line = line.decode('utf-8')
                                if not line.startswith('data: '):
                                    continue
                                    
                                try:
                                    json_data = json.loads(line[6:])
                                    if not json_data.get('choices'):
                                        continue
                                        
                                    delta = json_data['choices'][0].get('delta', {})
                                    if 'content' in delta:
                                        content = delta['content']
                                        full_response += content
                                        if index is not None:
                                            print(f"\r请求 #{index + 1} - 实时输出: {full_response}", end='', flush=True)
                                except json.JSONDecodeError:
                                    continue
                                    
                            if index is not None:
                                print()  # 换行
                            return {"choices": [{"message": {"content": full_response}}]}
                            
                        except Exception as e:
                            self.logger.error(f"流式响应处理错误: {str(e)}")
                            raise
                    else:
                        return response.json()
                else:
                    error_msg = f"请求失败，状态码: {response.status_code}, 响应: {response.text}"
                    self.logger.error(f"请求 #{index + 1 if index is not None else 'N/A'} - {error_msg}")
                    
            except requests.exceptions.Timeout:
                error_msg = f"请求超时 (timeout={self.process_config.timeout}s)"
                self.logger.error(f"请求 #{index + 1 if index is not None else 'N/A'} - {error_msg}")
                
            except requests.exceptions.RequestException as e:
                error_msg = f"请求异常: {str(e)}"
                self.logger.error(f"请求 #{index + 1 if index is not None else 'N/A'} - {error_msg}")

            if attempt < self.process_config.max_retries - 1:
                wait_time = self.process_config.retry_wait_time * (attempt + 1)  # 指数退避
                self.logger.info(f"请求 #{index + 1 if index is not None else 'N/A'} - 等待 {wait_time}s 后重试 ({attempt + 1}/{self.process_config.max_retries})")
                time.sleep(wait_time)
        
        raise Exception(f"请求失败，已达到最大重试次数 ({self.process_config.max_retries})")

    def process_request(self, entry: Dict[str, Any], index: int) -> Dict[str, Any]:
        try:
            # 从 loc 中提取主题名称，去掉数字并分割
            file_name = entry['loc'].split()[0].rstrip('0123456789') + '.jsonl'
            
            # 构建问题
            ti_question = entry.get("polished_ti_content", "")
            
            # 获取few-shot示例（如果启用）
            few_shot_examples = ""
            if self.model_config.prompt_config.max_shots > 0:
                few_shot_examples = self.get_few_shot_examples(
                    file_name, 
                    self.model_config.prompt_config.max_shots
                )
            
            # 使用新的配置方式构建请求参数
            payload = self.model_config.get_request_params(
                question=ti_question,
                few_shot_examples=few_shot_examples
            )
            
            # 使用统一的请求处理方法
            response_json = self.make_request(payload, index)
            
            if "choices" in response_json and response_json["choices"]:
                message = response_json["choices"][0].get("message", {})
                content = message.get("content", "").strip()
                if content:
                    entry["model_result"] = content
                    self.logger.info(f"请求 #{index + 1} - 结果: {content}")
                    return entry

        except Exception as e:
            self.logger.error(f"处理请求时发生错误: {str(e)}")

        entry["model_result"] = "Failed after retries"
        return entry

    def process_file(self, input_file: str) -> None:
        self.logger.info(f"开始处理文件: {input_file}")
        
        # 修改输出文件名格式
        base_name = os.path.basename(input_file)
        base_name = base_name.replace('.jsonl', '')  # 移除原文件的 .jsonl 后缀
        model_suffix = self.model_config.model_name.lower().replace(" ", "_")
        output_file = os.path.join(
            self.process_config.output_folder,
            f"{base_name}_{model_suffix}_out.jsonl"
        )
        
        if os.path.exists(output_file):
            self.logger.info(f"文件已存在，跳过处理: {output_file}")
            return

        try:
            # 读取输入文件
            with open(input_file, 'r', encoding='utf-8') as f:
                entries = [json.loads(line.strip()) for line in f if line.strip()]
            
            if not entries:
                self.logger.warning(f"文件为空: {input_file}")
                return
                
            # 记录第一个条目的提示词构建结果
            first_entry = entries[0]
            file_name = first_entry['loc'].split()[0].rstrip('0123456789') + '.jsonl'
            ti_question = first_entry.get("polished_ti_content", "")
            
            few_shot_examples = ""
            if self.model_config.prompt_config.max_shots > 0:
                few_shot_examples = self.get_few_shot_examples(
                    file_name, 
                    self.model_config.prompt_config.max_shots
                )
            
            payload = self.model_config.get_request_params(
                question=ti_question,
                few_shot_examples=few_shot_examples
            )
            
            # 使用分隔符使日志更清晰
            self.logger.info("\n" + "="*50)
            self.logger.info(f"文件 {base_name} 的提示词示例:")
            for msg in payload["messages"]:
                self.logger.info(f"\nRole: {msg['role']}")
                self.logger.info(f"Content:\n{msg['content']}")
            self.logger.info("\n" + "="*50 + "\n")

            # 处理所有条目
            with concurrent.futures.ThreadPoolExecutor(
                max_workers=self.process_config.batch_size
            ) as executor:
                futures = {
                    executor.submit(self.process_request, entry, idx): idx 
                    for idx, entry in enumerate(entries)
                }
                
                results = []
                for future in tqdm(
                    concurrent.futures.as_completed(futures),
                    total=len(entries),
                    desc=f"处理 {base_name}"
                ):
                    results.append(future.result())

            # 保存结果
            with open(output_file, 'w', encoding='utf-8') as f:
                for result in results:
                    f.write(json.dumps(result, ensure_ascii=False) + '\n')
            self.logger.info(f"结果已保存: {output_file}")

        except Exception as e:
            self.logger.error(f"处理文件失败 {input_file}: {str(e)}")

    def process_all_files(self) -> None:
        if not os.path.exists(self.process_config.output_folder):
            os.makedirs(self.process_config.output_folder)

        input_files = [
            os.path.join(self.process_config.input_folder, f)
            for f in os.listdir(self.process_config.input_folder)
            if f.endswith('.jsonl')
        ]

        for input_file in tqdm(input_files, desc="处理文件"):
            self.process_file(input_file)

    def get_pending_tasks(self) -> dict:
        """获取所有待处理任务
        Returns:
            dict: {
                'file_level': [文件名列表],  # 完全没有输出文件的任务
                'entry_level': {  # 已有输出文件但需要重试的任务
                    '输出文件名': {
                        'missing': [缺失的loc列表],
                        'failed': [失败的loc列表]
                    }
                }
            }
        """
        pending_tasks = {
            'file_level': [],
            'entry_level': {}
        }
        
        # 获取所有问题文件
        question_files = [f for f in os.listdir(self.process_config.input_folder) 
                         if f.endswith('.jsonl')]
        
        # 检查每个问题文件的状态
        for question_file in question_files:
            base_name = question_file.replace('.jsonl', '')
            model_suffix = self.model_config.model_name.lower().replace(" ", "_")
            output_file = f"{base_name}_{model_suffix}_out.jsonl"
            output_path = os.path.join(self.process_config.output_folder, output_file)
            
            # 如果输出文件不存在，添加到文件级任务
            if not os.path.exists(output_path):
                pending_tasks['file_level'].append(question_file)
                continue
                
            # 读取原始问题文件的所有loc
            question_locs = set()
            with open(os.path.join(self.process_config.input_folder, question_file), 
                     'r', encoding='utf-8') as f:
                for line in f:
                    data = json.loads(line.strip())
                    question_locs.add(data['loc'])
            
            # 检查输出文件中的条目
            output_locs = set()
            failed_locs = []
            with open(output_path, 'r', encoding='utf-8') as f:
                for line in f:
                    data = json.loads(line.strip())
                    output_locs.add(data['loc'])
                    if data['model_result'] == "Failed after retries":
                        failed_locs.append(data['loc'])
            
            # 找出缺失和失败的条目
            missing_locs = list(question_locs - output_locs)
            if missing_locs or failed_locs:
                pending_tasks['entry_level'][output_file] = {
                    'missing': missing_locs,
                    'failed': failed_locs,
                    'question_file': question_file
                }
        
        return pending_tasks
    
    def process_all(self):
        """处理所有待处理任务"""
        pending_tasks = self.get_pending_tasks()
        
        # 首先处理条目级任务（已有输出文件中的失败和缺失条目）
        for output_file, task_info in pending_tasks['entry_level'].items():
            self.logger.info(f"处理文件 {output_file} 中的条目级任务")
            
            # 读取原始问题
            questions = {}
            with open(os.path.join(self.process_config.input_folder, task_info['question_file']), 
                     'r', encoding='utf-8') as f:
                for line in f:
                    data = json.loads(line.strip())
                    questions[data['loc']] = data
            
            # 读取现有输出
            outputs = []
            with open(os.path.join(self.process_config.output_folder, output_file), 
                     'r', encoding='utf-8') as f:
                outputs = [json.loads(line.strip()) for line in f]
            
            # 处理失败和缺失的条目
            all_pending_locs = set(task_info['failed'] + task_info['missing'])
            
            with concurrent.futures.ThreadPoolExecutor(
                max_workers=self.process_config.batch_size
            ) as executor:
                futures = {}
                for idx, loc in enumerate(all_pending_locs):
                    if loc in questions:
                        futures[executor.submit(
                            self.process_request, 
                            questions[loc],
                            idx  # 添加索引参数
                        )] = loc
                
                for future in tqdm(
                    concurrent.futures.as_completed(futures),
                    total=len(futures),
                    desc=f"处理 {output_file} 的待处理条目"
                ):
                    result = future.result()
                    # 更新或添加结果
                    updated = False
                    for i, entry in enumerate(outputs):
                        if entry['loc'] == result['loc']:
                            outputs[i] = result
                            updated = True
                            break
                    if not updated:
                        outputs.append(result)
            
            # 保存更新后的结果
            with open(os.path.join(self.process_config.output_folder, output_file), 
                     'w', encoding='utf-8') as f:
                for entry in outputs:
                    f.write(json.dumps(entry, ensure_ascii=False) + '\n')
        
        # 然后处理文件级任务（完全没有输出文件的任务）
        for question_file in pending_tasks['file_level']:
            self.logger.info(f"处理文件级任务: {question_file}")
            self.process_file(os.path.join(self.process_config.input_folder, question_file))