#!/usr/bin/env python3
"""
Create heatmap for Tibetan MMLU evaluation results
Shows all 4 models across 67 subjects using concern_all_answer metrics
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend

# Set style
matplotlib.rcParams['font.family'] = 'DejaVu Sans'

def load_model_data(model_id):
    """Load concern_all_answer metrics for a model"""
    csv_path = f"../model_answer/{model_id}_eval_res/{model_id}_concern_all_answer_metrics_results.csv"
    df = pd.read_csv(csv_path)
    return df

def clean_percentage(value):
    """Convert percentage string to float"""
    if isinstance(value, str):
        return float(value.rstrip('%'))
    return float(value)

def create_heatmap(metric_column, metric_name, output_filename, cmap='RdYlGn'):
    """Create a heatmap showing all models across all subjects"""

    models = {
        'gemini-2-5-pro': 'Gemini 2.5 Pro',
        'gemini-2-5-flash': 'Gemini 2.5 Flash',
        'claude-opus-4-1': 'Claude Opus 4.1',
        'claude-sonnet-4-5': 'Claude Sonnet 4.5'
    }

    # Load data for all models
    data_dict = {}
    subjects = None

    for model_id, model_label in models.items():
        df = load_model_data(model_id)
        if subjects is None:
            subjects = df['File Name'].tolist()

        # Convert percentage to float
        values = df[metric_column].apply(clean_percentage).tolist()
        data_dict[model_label] = values

    # Create DataFrame for heatmap
    heatmap_df = pd.DataFrame(data_dict, index=subjects)

    # Create figure
    fig, ax = plt.subplots(figsize=(12, 28))

    # Create heatmap
    im = ax.imshow(heatmap_df.values, cmap=cmap, aspect='auto', vmin=0, vmax=100)

    # Set ticks
    ax.set_xticks(np.arange(len(models)))
    ax.set_yticks(np.arange(len(subjects)))

    # Set tick labels
    ax.set_xticklabels(models.values(), fontsize=12, fontweight='bold')

    # Format subject names: replace underscores with spaces and title case
    formatted_subjects = [s.replace('_', ' ').title() for s in subjects]
    ax.set_yticklabels(formatted_subjects, fontsize=9)

    # Rotate the tick labels for better readability
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")

    # Add colorbar
    cbar = plt.colorbar(im, ax=ax, pad=0.02)
    cbar.set_label(f'{metric_name} (%)', rotation=270, labelpad=25, fontsize=12, fontweight='bold')
    cbar.ax.tick_params(labelsize=10)

    # Add text annotations with values
    for i in range(len(subjects)):
        for j in range(len(models)):
            value = heatmap_df.values[i, j]
            # Choose text color based on background
            text_color = 'white' if value < 50 else 'black'
            text = ax.text(j, i, f'{value:.0f}',
                          ha="center", va="center", color=text_color,
                          fontsize=7, fontweight='bold')

    # Set title
    ax.set_title(f'Tibetan MMLU: {metric_name} Heatmap Across 67 Subjects\n(Concern All Answer Method, 0-shot Evaluation)',
                fontsize=16, fontweight='bold', pad=20)

    # Add grid
    ax.set_xticks(np.arange(len(models)) - 0.5, minor=True)
    ax.set_yticks(np.arange(len(subjects)) - 0.5, minor=True)
    ax.grid(which="minor", color="white", linestyle='-', linewidth=2)

    plt.tight_layout()

    # Save figure
    output_path = f"../model_answer/{output_filename}"
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✓ Saved: {output_path}")
    plt.close()

def create_compact_heatmap(metric_column, metric_name, output_filename):
    """Create a more compact heatmap without text annotations"""

    models = {
        'gemini-2-5-pro': 'Gemini 2.5 Pro',
        'gemini-2-5-flash': 'Gemini 2.5 Flash',
        'claude-opus-4-1': 'Claude Opus 4.1',
        'claude-sonnet-4-5': 'Claude Sonnet 4.5'
    }

    # Load data for all models
    data_dict = {}
    subjects = None

    for model_id, model_label in models.items():
        df = load_model_data(model_id)
        if subjects is None:
            subjects = df['File Name'].tolist()

        # Convert percentage to float
        values = df[metric_column].apply(clean_percentage).tolist()
        data_dict[model_label] = values

    # Create DataFrame for heatmap
    heatmap_df = pd.DataFrame(data_dict, index=subjects)

    # Create figure
    fig, ax = plt.subplots(figsize=(10, 24))

    # Create heatmap
    im = ax.imshow(heatmap_df.values, cmap='RdYlGn', aspect='auto', vmin=0, vmax=100)

    # Set ticks
    ax.set_xticks(np.arange(len(models)))
    ax.set_yticks(np.arange(len(subjects)))

    # Set tick labels
    ax.set_xticklabels(models.values(), fontsize=11, fontweight='bold')

    # Format subject names
    formatted_subjects = [s.replace('_', ' ').title() for s in subjects]
    ax.set_yticklabels(formatted_subjects, fontsize=8)

    # Rotate the tick labels
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")

    # Add colorbar
    cbar = plt.colorbar(im, ax=ax, pad=0.02)
    cbar.set_label(f'{metric_name} (%)', rotation=270, labelpad=20, fontsize=11, fontweight='bold')
    cbar.ax.tick_params(labelsize=9)

    # Set title
    ax.set_title(f'Tibetan MMLU: {metric_name} Across 67 Subjects\n(Concern All Answer Method, 0-shot)',
                fontsize=14, fontweight='bold', pad=15)

    # Add grid
    ax.set_xticks(np.arange(len(models)) - 0.5, minor=True)
    ax.set_yticks(np.arange(len(subjects)) - 0.5, minor=True)
    ax.grid(which="minor", color="white", linestyle='-', linewidth=1.5)

    plt.tight_layout()

    # Save figure
    output_path = f"../model_answer/{output_filename}"
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✓ Saved: {output_path}")
    plt.close()

def create_transposed_heatmap(metric_column, metric_name, output_filename):
    """Create a wide heatmap with subjects on x-axis and models on y-axis"""

    models = {
        'gemini-2-5-pro': 'Gemini 2.5 Pro',
        'gemini-2-5-flash': 'Gemini 2.5 Flash',
        'claude-opus-4-1': 'Claude Opus 4.1',
        'claude-sonnet-4-5': 'Claude Sonnet 4.5'
    }

    # Load data for all models
    data_dict = {}
    subjects = None

    for model_id, model_label in models.items():
        df = load_model_data(model_id)
        if subjects is None:
            subjects = df['File Name'].tolist()

        # Convert percentage to float
        values = df[metric_column].apply(clean_percentage).tolist()
        data_dict[model_label] = values

    # Create DataFrame for heatmap (transposed)
    heatmap_df = pd.DataFrame(data_dict, index=subjects).T

    # Create figure
    fig, ax = plt.subplots(figsize=(28, 6))

    # Create heatmap
    im = ax.imshow(heatmap_df.values, cmap='RdYlGn', aspect='auto', vmin=0, vmax=100)

    # Set ticks
    ax.set_yticks(np.arange(len(models)))
    ax.set_xticks(np.arange(len(subjects)))

    # Set tick labels
    ax.set_yticklabels(models.values(), fontsize=12, fontweight='bold')

    # Format subject names
    formatted_subjects = [s.replace('_', ' ').title() for s in subjects]
    ax.set_xticklabels(formatted_subjects, fontsize=9, rotation=90, ha='right')

    # Add colorbar
    cbar = plt.colorbar(im, ax=ax, pad=0.01, orientation='horizontal')
    cbar.set_label(f'{metric_name} (%)', labelpad=10, fontsize=12, fontweight='bold')
    cbar.ax.tick_params(labelsize=10)

    # Set title
    ax.set_title(f'Tibetan MMLU: {metric_name} Across 67 Subjects\n(Concern All Answer Method, 0-shot)',
                fontsize=16, fontweight='bold', pad=15)

    # Add grid
    ax.set_yticks(np.arange(len(models)) - 0.5, minor=True)
    ax.set_xticks(np.arange(len(subjects)) - 0.5, minor=True)
    ax.grid(which="minor", color="white", linestyle='-', linewidth=2)

    plt.tight_layout()

    # Save figure
    output_path = f"../model_answer/{output_filename}"
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✓ Saved: {output_path}")
    plt.close()

def main():
    """Generate all heatmaps"""
    print("=" * 70)
    print("Generating Heatmaps for Tibetan MMLU Evaluation")
    print("=" * 70)
    print()

    heatmaps = [
        ('Accuracy', 'Accuracy',
         'concern_all_answer_accuracy_heatmap.png',
         'concern_all_answer_accuracy_heatmap_compact.png',
         'concern_all_answer_accuracy_heatmap_wide.png'),
        ('Response Rate', 'Response Rate',
         'concern_all_answer_response_rate_heatmap.png',
         'concern_all_answer_response_rate_heatmap_compact.png',
         'concern_all_answer_response_rate_heatmap_wide.png'),
        ('Conditional Accuracy', 'Conditional Accuracy',
         'concern_all_answer_conditional_accuracy_heatmap.png',
         'concern_all_answer_conditional_accuracy_heatmap_compact.png',
         'concern_all_answer_conditional_accuracy_heatmap_wide.png')
    ]

    for metric_column, metric_name, output_annotated, output_compact, output_wide in heatmaps:
        print(f"Creating {metric_name} heatmaps...")

        print(f"  - Annotated version (with values)...")
        create_heatmap(metric_column, metric_name, output_annotated)

        print(f"  - Compact version (without values)...")
        create_compact_heatmap(metric_column, metric_name, output_compact)

        print(f"  - Wide version (transposed)...")
        create_transposed_heatmap(metric_column, metric_name, output_wide)

        print()

    print("=" * 70)
    print("✓ All heatmaps generated successfully!")
    print("Charts saved in: ../model_answer/")
    print("=" * 70)

if __name__ == "__main__":
    main()
