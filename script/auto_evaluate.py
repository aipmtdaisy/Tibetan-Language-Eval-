import os
import sys
import json
import csv
import pandas as pd
from typing import List, Tuple

# 导入评估脚本和配置加载器
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config_loader import load_config

# 1.0 找出一个字母
def calculate_metrics_direct_answer(file_path: str, exclude_list: List[str], output_file_path: str) -> Tuple[float, float, float]:
    total_count = 0  # 总条目数
    valid_response_count = 0  # "model_result"中有效响应的数量
    correct_count = 0  # 答案正确的数量

    # 定义英文和藏文选项集
    english_choices = {"A", "B", "C", "D"}
    tibetan_choices = {"ཀ", "ཁ", "ག", "ང"}
    # 藏文到英文的映射
    tibetan_to_english = {"ཀ": "A", "ཁ": "B", "ག": "C", "ང": "D"}

    # 打开输出文件以保存结果
    with open(output_file_path, 'w', encoding='utf-8') as output_file:
        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                total_count += 1
                data = json.loads(line)
                answer = data.get("answer", "")
                model_result = data.get("model_result", "")

                # 过滤思维链格式
                model_result = filter_cot_patterns(model_result)

                # 从 model_result 中移除排除列表中的内容
                for excluded in exclude_list:
                    model_result = model_result.replace(excluded, "")

                # 优先检查英文字母
                found_english = [choice for choice in english_choices if choice in model_result]
                if len(found_english) == 1:
                    final_answer = found_english
                else:
                    # 如果没有找到英文字母，检查藏文字母
                    found_tibetan = [choice for choice in tibetan_choices if choice in model_result]
                    if len(found_tibetan) == 1:
                        final_answer = [tibetan_to_english[found_tibetan[0]]]
                    else:
                        final_answer = []

                # 将过滤后的结果保存到JSONL文件中
                data["direct_answer"] = final_answer
                output_file.write(json.dumps(data, ensure_ascii=False) + '\n')

                # 检查是否有效响应
                if len(final_answer) == 1:
                    valid_response_count += 1
                    if final_answer[0] == answer:  # 如果该选项与正确答案一致
                        correct_count += 1

    # 计算指标
    response_rate = valid_response_count / total_count if total_count > 0 else 0
    accuracy = correct_count / total_count if total_count > 0 else 0
    conditional_accuracy = correct_count / valid_response_count if valid_response_count > 0 else 0

    return response_rate, accuracy, conditional_accuracy

# 2.0 过滤 乱序A B C D 取模
def calculate_metrics_concern_all_answer(file_path: str, exclude_list: List[str], output_file_path: str) -> Tuple[float, float, float]:
    total_count = 0  # 总条目数
    valid_response_count = 0  # "model_result"中有效响应的数量
    correct_count = 0  # 答案正确的数量

    # 定义英文和藏文选项集
    english_choices = {"A", "B", "C", "D"}
    tibetan_choices = {"ཀ", "ཁ", "ག", "ང"}
    # 藏文到英文的映射
    tibetan_to_english = {"ཀ": "A", "ཁ": "B", "ག": "C", "ང": "D"}

    # 打开输出文件以保存结果
    with open(output_file_path, 'w', encoding='utf-8') as output_file:
        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                total_count += 1
                data = json.loads(line)
                answer = data.get("answer", "")
                model_result = data.get("model_result", "")

                # 过滤思维链格式
                model_result = filter_cot_patterns(model_result)

                # 从 model_result 中移除排除列表中的内容
                for excluded in exclude_list:
                    model_result = model_result.replace(excluded, "")

                # 第一步：提取所有按顺序出现的选项字母，优先英文
                def extract_all_choices(result: str) -> List[str]:
                    # 先提取英文字母
                    english = [ch for ch in result if ch in english_choices]
                    if english:  # 如果找到英文字母，直接返回
                        return english
                    # 没有英文字母时，提取并转换藏文字母
                    return [tibetan_to_english[ch] for ch in result if ch in tibetan_choices]

                all_choices = extract_all_choices(model_result)

                # 第二步：去除完整的 ABCD 组合（乱序也算）
                def remove_abcd_combinations(choices: List[str]) -> List[str]:
                    filtered = []
                    buffer = []
                    for ch in choices:
                        buffer.append(ch)
                        if len(buffer) == 4 and set(buffer) == english_choices:
                            buffer = []  # 清空 buffer 表示去除一个完整组合
                        elif len(buffer) > 4:
                            filtered.extend(buffer[:-3])  # 保留超出部分
                            buffer = buffer[-3:]
                    filtered.extend(buffer)  # 添加剩余未处理部分
                    return filtered

                filtered_choices = remove_abcd_combinations(all_choices)

                # 第三步：判断模型的最终答案
                def determine_final_answer(filtered: List[str]) -> List[str]:
                    unique_choices = set(filtered)
                    if len(unique_choices) == 1:  # 只有一个字母
                        return list(unique_choices)
                    elif len(unique_choices) > 1:  # 多个不同字母
                        return []  # 无效
                    return filtered  # 直接返回剩余的结果

                final_answer = determine_final_answer(filtered_choices)

                # 将过滤后的结果保存到JSONL文件中
                data["filtered_model_result"] = final_answer
                output_file.write(json.dumps(data, ensure_ascii=False) + '\n')

                # 检查"model_result"中只出现了一个有效选项字母
                if len(final_answer) == 1:
                    valid_response_count += 1
                    if final_answer[0] == answer:  # 如果该选项与正确答案一致
                        correct_count += 1

    # 计算指标
    response_rate = valid_response_count / total_count if total_count > 0 else 0
    accuracy = correct_count / total_count if total_count > 0 else 0
    conditional_accuracy = correct_count / valid_response_count if valid_response_count > 0 else 0

    return response_rate, accuracy, conditional_accuracy

def process_folder(folder_path: str, exclude_list: List[str], output_folder: str, filtered_prefix: str = None):
    # 提取文件夹名去掉 "_out" 后缀
    folder_name = os.path.basename(folder_path.rstrip("/"))
    if folder_name.endswith("_out"):
        folder_name = folder_name[:-4]

    # 根据评估方法选择输出文件名和计算函数
    if filtered_prefix == "direct_":
        output_csv = os.path.join(output_folder, f"{folder_name}_direct_metrics_results.csv")
        calculate_func = calculate_metrics_direct_answer
    else:
        output_csv = os.path.join(output_folder, f"{folder_name}_concern_all_answer_metrics_results.csv")
        calculate_func = calculate_metrics_concern_all_answer

    # 确保输出文件夹存在
    os.makedirs(output_folder, exist_ok=True)

    # 写入CSV文件
    with open(output_csv, mode="w", encoding="utf-8", newline="") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["File Name", "Response Rate", "Conditional Accuracy", "Accuracy"])

        # 遍历文件夹中的所有文件
        for file_name in os.listdir(folder_path):
            if file_name.endswith(".jsonl"):
                file_path = os.path.join(folder_path, file_name)

                # 输出文件路径
                prefix = filtered_prefix if filtered_prefix else "filtered_"
                output_file_path = os.path.join(output_folder, f"{prefix}{file_name}")

                # 提取文件名前缀，保留到模型名称之前的部分
                base_name = "_".join(file_name.split("_")[:-2])  # 去掉最后两个部分（模型名和out.jsonl）

                # 计算指标
                response_rate, accuracy, conditional_accuracy = calculate_func(file_path, exclude_list, output_file_path)

                # 写入CSV文件
                writer.writerow([
                    base_name,
                    f"{response_rate:.2%}",
                    f"{conditional_accuracy:.2%}",
                    f"{accuracy:.2%}"
                ])

def auto_evaluate_results(model_id: str):
    """自动评估模型结果
    Args:
        model_id: 模型ID，用于定位输出文件夹
    """
    # 加载配置
    _, _, _, evaluation_config = load_config()
    
    # 构建输入和输出文件夹路径
    input_folder = f"../model_answer/{model_id}"
    output_folder = evaluation_config.output_folder_template.format(model_id=model_id)
    
    # 处理文件夹，生成评估结果
    for method_name, method_config in evaluation_config.methods.items():
        if not method_config.enabled:
            continue
            
        # 设置过滤后的答案文件前缀
        filtered_prefix = method_config.filtered_file_prefix
        
        # 处理文件夹，生成评估结果
        process_folder(input_folder, evaluation_config.exclude_list, output_folder, filtered_prefix)
        print(f"已完成{method_name}评估，结果已保存到 {output_folder}")
        
        # 计算通用类别结果
        score_file = os.path.join(output_folder, method_config.metrics_file_template.format(model_id=model_id))
        
        if not os.path.exists(score_file):
            print(f"警告：找不到评估文件 {score_file}")
            continue
            
        # 创建 general 子文件夹
        general_folder = os.path.join(output_folder, evaluation_config.general_category_folder)
        os.makedirs(general_folder, exist_ok=True)
        
        # 计算通用类别平均分
        try:
            df = pd.read_csv(score_file)
            category_averages = calculate_category_average(df, category_mapping)
            
            # 转换为DataFrame并保存
            result_df = pd.DataFrame(category_averages)
            output_file = os.path.join(general_folder, f"{model_id}_{method_name}_category_averages.csv")
            result_df.to_csv(output_file, index=False)
            
            print(f"已生成{method_name}通用类别评估结果：{output_file}")
        except Exception as e:
            print(f"计算{method_name}通用类别结果时出错：{str(e)}")

# 大类及小类分类字典
category_mapping = {
    "China specific": [
        "ancient_chinese", "traditional_chinese_medicine", "modern_chinese", "high_school_politics",
        "ethnology", "elementary_commonsense", "elementary_chinese", "education", "construction_project_management",
        "chinese_teacher_qualification", "chinese_literature", "chinese_history", "chinese_foreign_policy",
        "chinese_food_culture", "chinese_driving_rule", "chinese_civil_service_exam"
    ],
    "Other": [
        "sports_science", "professional_medicine", "nutrition", "legal_and_moral_basis", "human_sexuality",
        "food_science", "elementary_it", "computer_security", "college_medicine", "clinical_knowledge", "agronomy"
    ],
    "Social Sciences": [
        "sociology", "security_study", "public_relations", "professional_psychology", "professional_accounting",
        "marketing", "management", "journalism", "high_school_geography", "economics", "college_education",
        "business_ethics"
    ],
    "Humanities": [
        "world_religions", "world_history", "professional_law", "philosophy", "marxist_theory", "logical",
        "jurisprudence", "international_law", "global_facts", "college_law", "arts"
    ],
    "STEM": [
        "virology", "machine_learning", "high_school_physics", "high_school_mathematics", "high_school_chemistry",
        "high_school_biology", "genetics", "elementary_mathematics", "electrical_engineering", "conceptual_physics",
        "computer_science", "college_medical_statistics", "college_mathematics", "college_engineering_hydrology",
        "college_actuarial_science", "astronomy", "anatomy"
    ]
}

# 计算每列的平均得分（包括Response Rate、Conditional Accuracy、Accuracy）
def calculate_category_average(df, category_mapping):
    category_averages = []

    for category, files in category_mapping.items():
        category_scores = {
            "Response Rate": [],
            "Conditional Accuracy": [],
            "Accuracy": []
        }

        # 遍历每个小类文件
        for file in files:
            file_score = df[df['File Name'] == file]
            if not file_score.empty:
                # 取得各列的得分
                category_scores["Response Rate"].append(float(file_score['Response Rate'].values[0].strip('%')) / 100)
                category_scores["Conditional Accuracy"].append(float(file_score['Conditional Accuracy'].values[0].strip('%')) / 100)
                category_scores["Accuracy"].append(float(file_score['Accuracy'].values[0].strip('%')) / 100)

        # 计算大类的平均得分
        if category_scores["Response Rate"]:
            category_averages.append({
                "Category": category,
                "Response Rate Average": f"{(sum(category_scores['Response Rate']) / len(category_scores['Response Rate'])) * 100:.2f}%",
                "Conditional Accuracy Average": f"{(sum(category_scores['Conditional Accuracy']) / len(category_scores['Conditional Accuracy'])) * 100:.2f}%",
                "Accuracy Average": f"{(sum(category_scores['Accuracy']) / len(category_scores['Accuracy'])) * 100:.2f}%"
            })

    return category_averages

# 定义思维链标签列表
COT_TAGS = [
    ('<think>', '</think>'),
    ('<reasoning>', '</reasoning>'),
    ('<thought>', '</thought>'),
    ('<analysis>', '</analysis>'),
    ('<step>', '</step>')
]

def filter_cot_patterns(text: str) -> str:
    """过滤常见思维链格式"""
    result = text
    
    # 过滤 XML 标签格式的思维链
    import re
    for start_tag, end_tag in COT_TAGS:
        pattern = f'{start_tag}.*?{end_tag}'
        result = re.sub(pattern, '', result, flags=re.DOTALL)
    
    return result

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("用法：python auto_evaluate.py <model_id>")
        sys.exit(1)
        
    model_id = sys.argv[1]
    auto_evaluate_results(model_id)