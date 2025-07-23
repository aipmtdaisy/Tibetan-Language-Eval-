# Ti-MMLU Evaluation System

## Introduction

Ti-MMLU is a subset of the TLUE (Tibetan Language Understanding Evaluation) benchmark, focusing on Tibetan-Chinese bilingual multiple-choice questions evaluation. The evaluation system supports both English (A, B, C, D) and Tibetan (ཀ, ཁ, ག, ང) option recognition and evaluation. For more details, please refer to our paper: [TLUE Paper](https://arxiv.org/pdf/2503.12051)

## Dataset

Currently, the `Ti-MMLU_subset670` dataset is available. The complete dataset will be released later.

## System Overview

The system consists of two main components:
1. Model Execution (`run_models.py`): Run models on the test set
2. Result Evaluation (`auto_evaluate.py`): Analyze and evaluate model outputs

## Configuration Guide

The system uses `config.yaml` for configuration, which includes the following sections:

1. Prompt Configuration (prompt_config)
   - `max_shots`: Number of few-shot examples used in each prompt
   - `system_message`: System message (supports Chinese/Tibetan)
   - `user_template`: User prompt template
   - `few_shot_template`: Format template for few-shot examples

2. Process Configuration (process_config)
   - `input_folder`: Input folder path
   - `output_folder_template`: Output folder template
   - `few_shot_folder`: Few-shot examples folder path
   - `batch_size`: Batch processing size
   - `max_retries`: Maximum retry attempts
   - `timeout`: Request timeout
   - `retry_wait_time`: Retry wait time

3. Evaluation Configuration (evaluation_config)
   - Supports direct answer evaluation and comprehensive answer evaluation
   - Configurable evaluation result output paths and filename templates

4. Model Configuration (model_configs)
   - Supports multiple model configurations
   - Each model can be configured with name, API address, temperature, etc.

## Usage

1. Run models and generate results:
```python
# Basic usage
python run_models.py

# Use custom configuration file
python run_models.py --config path/to/config.yaml
```

2. Evaluate results:
```python
# After model execution, evaluate results
python auto_evaluate.py <model_id>
```

## Evaluation Methods

### 1. Direct Answer Evaluation
- Function: Extract single option letter from model response
- Priority: Prioritize English letters, fall back to Tibetan letters if no English letters found
- Output: Extracted single option (converted to English letter)

### 2. Comprehensive Answer Evaluation
- Function: Analyze all option letters in model response
- Processing: Remove complete ABCD combinations (including shuffled), retain remaining options
- Priority: Process English letters first, then Tibetan letters if no English letters found
- Output: Processed single option (if exists)

## Evaluation Metrics

The system calculates the following metrics:

1. Response Rate
   - Definition: Number of valid responses / Total number of questions

2. Accuracy
   - Definition: Number of correct answers / Total number of questions

3. Conditional Accuracy
   - Definition: Number of correct answers / Number of valid responses

## Output Files

1. Evaluation Result Files
   - `{model_id}_direct_metrics_results.csv`: Direct answer evaluation results
   - `{model_id}_concern_all_answer_metrics_results.csv`: Comprehensive answer evaluation results

2. General Category Results
   - Location: `../model_answer/{model_id}_eval_res/general/`
   - Files: `{model_id}_direct_category_averages.csv`, `{model_id}_concern_all_answer_category_averages.csv`

## Notes

1. Option Recognition Priority
   - Prioritize English letters (A, B, C, D)
   - Only recognize Tibetan letters (ཀ, ཁ, ག, ང) when no English letters are found

2. Answer Processing
   - Tibetan options are automatically converted to corresponding English letters
   - System automatically filters out invalid answer formats

3. Configuration File
   - Ensure correct configuration in `config.yaml` before running
   - Pay special attention to API key and address settings in model configuration

[查看中文版](./README_zh.md)