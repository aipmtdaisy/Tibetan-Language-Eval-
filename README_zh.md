# Ti-MMLU 评估系统

## 简介

Ti-MMLU 是 TLUE（藏语理解评估）基准测试的一个子集，专注于藏汉双语的多选题评估。评估系统支持英文（A、B、C、D）和藏文（ཀ、ཁ、ག、ང）选项的识别和评估。详细信息请参考我们的论文：[TLUE论文](https://arxiv.org/pdf/2503.12051)

## 数据集

目前开放 `Ti-MMLU_subset670` 数据集，完整数据集将在后续开放。

## 系统概述

系统包含两个主要组件：
1. 模型运行（`run_models.py`）：在测试集上执行模型
2. 结果评估（`auto_evaluate.py`）：分析和评估模型输出

## 配置说明

系统使用 `config.yaml` 进行配置，主要包含以下部分：

1. 提示词配置 (prompt_config)
   - `max_shots`: 每次提示中使用的few-shot示例数量
   - `system_message`: 系统消息（支持中文/藏文）
   - `user_template`: 用户提示模板
   - `few_shot_template`: few-shot示例的格式模板

2. 处理配置 (process_config)
   - `input_folder`: 输入文件夹路径
   - `output_folder_template`: 输出文件夹模板
   - `few_shot_folder`: few-shot示例文件夹路径
   - `batch_size`: 批处理大小
   - `max_retries`: 最大重试次数
   - `timeout`: 请求超时时间
   - `retry_wait_time`: 重试等待时间

3. 评估配置 (evaluation_config)
   - 支持直接答案评估和全面答案评估
   - 可配置评估结果输出路径和文件名模板

4. 模型配置 (model_configs)
   - 支持配置多个模型
   - 每个模型可设置名称、API地址、温度等参数

## 使用方法

1. 运行模型并生成结果：
```python
# 基本用法
python run_models.py

# 使用自定义配置文件
python run_models.py --config path/to/config.yaml
```

2. 评估结果：
```python
# 在模型执行完成后，评估结果
python auto_evaluate.py <model_id>
```

## 评估方法

### 1. 直接答案评估
- 功能：从模型回答中提取单个选项字母
- 优先级：优先识别英文字母，若无英文字母则识别藏文字母
- 输出：提取到的单个选项（转换为英文字母）

### 2. 全面答案评估
- 功能：分析模型回答中的所有选项字母
- 处理：去除完整的ABCD组合（包括乱序），保留剩余选项
- 优先级：优先处理英文字母，若无英文字母则处理藏文字母
- 输出：处理后的单个选项（如果存在）

## 评估指标

系统计算以下指标：

1. 响应率
   - 定义：有效答案数量 / 总问题数量

2. 准确率
   - 定义：正确答案数量 / 总问题数量

3. 条件准确率
   - 定义：正确答案数量 / 有效答案数量

## 输出文件

1. 评估结果文件
   - `{model_id}_direct_metrics_results.csv`：直接答案评估结果
   - `{model_id}_concern_all_answer_metrics_results.csv`：全面答案评估结果

2. 通用类别结果
   - 位置：`../model_answer/{model_id}_eval_res/general/`
   - 文件：`{model_id}_direct_category_averages.csv`, `{model_id}_concern_all_answer_category_averages.csv`

## 注意事项

1. 选项识别优先级
   - 优先识别英文字母 (A, B, C, D)
   - 仅在没有英文字母时才识别藏文字母 (ཀ, ཁ, ག, ང)

2. 答案处理
   - 藏文选项会自动转换为对应的英文字母
   - 系统会自动过滤掉无效的答案格式

3. 配置文件
   - 运行前请确保 `config.yaml` 中的配置正确
   - 特别注意模型配置部分的API密钥和地址设置

[View English Version](./README.md)