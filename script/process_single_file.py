#!/usr/bin/env python3
"""
Process a single test file for specific models
"""
import sys
import os
from config_loader import load_config
from logger import LoggerManager
from model_processor import ModelProcessor

def process_single_file(model_id, file_name):
    """Process a single file for a specific model"""
    # Load configuration
    model_configs, prompt_config, process_config, _ = load_config()

    if model_id not in model_configs:
        print(f"Error: Model {model_id} not found in config")
        return False

    # Get model config
    model_config = model_configs[model_id]
    model_config.prompt_config = prompt_config

    # Set output folder
    process_config.output_folder = process_config.output_folder_template.format(
        model_id=model_id,
        max_shots=model_config.prompt_config.max_shots
    )

    # Initialize logger
    logger_manager = LoggerManager(f"{model_id}_processor")

    # Create processor
    processor = ModelProcessor(model_config, process_config, logger_manager)

    # Process the single file
    input_file = os.path.join(process_config.input_folder, file_name)
    if not os.path.exists(input_file):
        print(f"Error: Input file not found: {input_file}")
        return False

    print(f"Processing {file_name} for {model_id}...")
    processor.process_file(input_file)
    print(f"Completed processing {file_name} for {model_id}")

    return True

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python process_single_file.py <model_id> <file_name>")
        print("Example: python process_single_file.py gemini-2-5-pro college_actuarial_science.jsonl")
        sys.exit(1)

    model_id = sys.argv[1]
    file_name = sys.argv[2]

    success = process_single_file(model_id, file_name)
    sys.exit(0 if success else 1)
