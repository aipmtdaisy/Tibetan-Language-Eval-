#!/usr/bin/env python3
"""
Create radar charts for Tibetan MMLU evaluation results
Compares all 4 models across 5 high-level categories using concern_all_answer metrics
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend

# Set style
matplotlib.rcParams['font.family'] = 'DejaVu Sans'

def load_category_data(model_id):
    """Load category averages for a model"""
    csv_path = f"../model_answer/{model_id}_eval_res/general/{model_id}_concern_all_answer_category_averages.csv"
    df = pd.read_csv(csv_path)
    return df

def clean_percentage(value):
    """Convert percentage string to float"""
    if isinstance(value, str):
        return float(value.rstrip('%'))
    return float(value)

def create_radar_chart(metric_column, title, output_filename):
    """Create a radar chart comparing all 4 models for a specific metric across 5 categories"""

    models = {
        'gemini-2-5-pro': {'color': '#4285F4', 'label': 'Gemini 2.5 Pro'},
        'gemini-2-5-flash': {'color': '#34A853', 'label': 'Gemini 2.5 Flash'},
        'claude-opus-4-1': {'color': '#EA4335', 'label': 'Claude Opus 4.1'},
        'claude-sonnet-4-5': {'color': '#FBBC04', 'label': 'Claude Sonnet 4.5'}
    }

    # Load data for first model to get category names
    first_model = list(models.keys())[0]
    df_first = load_category_data(first_model)
    categories = df_first['Category'].tolist()

    # Number of variables
    num_vars = len(categories)

    # Compute angle for each axis
    angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
    angles += angles[:1]  # Close the plot

    # Create figure
    fig, ax = plt.subplots(figsize=(12, 12), subplot_kw=dict(projection='polar'))

    # Plot each model
    for model_id, style in models.items():
        df = load_category_data(model_id)

        # Convert percentage strings to float
        values = df[metric_column].apply(clean_percentage).tolist()
        values += values[:1]  # Close the plot

        ax.plot(angles, values, 'o-', linewidth=2.5,
                label=style['label'], color=style['color'], markersize=8)
        ax.fill(angles, values, alpha=0.15, color=style['color'])

    # Fix axis to go clockwise and start at top
    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)

    # Set category labels
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories, fontsize=13, fontweight='bold')

    # Set y-axis limits and labels
    ax.set_ylim(0, 100)
    ax.set_yticks([20, 40, 60, 80, 100])
    ax.set_yticklabels(['20%', '40%', '60%', '80%', '100%'], fontsize=10)

    # Add grid
    ax.grid(True, alpha=0.3, linestyle='--', linewidth=1)

    # Add legend
    ax.legend(loc='upper right', bbox_to_anchor=(1.35, 1.1), fontsize=12, framealpha=0.95)

    # Add title
    plt.title(title, fontsize=16, fontweight='bold', pad=30, y=1.08)

    plt.tight_layout()

    # Save figure
    output_path = f"../model_answer/{output_filename}"
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✓ Saved: {output_path}")
    plt.close()

def create_combined_radar_chart():
    """Create a comprehensive radar chart with all three metrics in subplots"""

    models = {
        'gemini-2-5-pro': {'color': '#4285F4', 'label': 'Gemini 2.5 Pro'},
        'gemini-2-5-flash': {'color': '#34A853', 'label': 'Gemini 2.5 Flash'},
        'claude-opus-4-1': {'color': '#EA4335', 'label': 'Claude Opus 4.1'},
        'claude-sonnet-4-5': {'color': '#FBBC04', 'label': 'Claude Sonnet 4.5'}
    }

    # Load data for first model to get category names
    first_model = list(models.keys())[0]
    df_first = load_category_data(first_model)
    categories = df_first['Category'].tolist()

    # Number of variables
    num_vars = len(categories)

    # Compute angle for each axis
    angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
    angles += angles[:1]  # Close the plot

    # Create figure with 3 subplots (1 row, 3 columns)
    fig = plt.figure(figsize=(20, 7))

    metrics = [
        ('Response Rate Average', 'Response Rate'),
        ('Conditional Accuracy Average', 'Conditional Accuracy'),
        ('Accuracy Average', 'Overall Accuracy')
    ]

    for idx, (metric_column, metric_title) in enumerate(metrics):
        ax = fig.add_subplot(1, 3, idx + 1, projection='polar')

        # Plot each model
        for model_id, style in models.items():
            df = load_category_data(model_id)

            # Convert percentage strings to float
            values = df[metric_column].apply(clean_percentage).tolist()
            values += values[:1]  # Close the plot

            ax.plot(angles, values, 'o-', linewidth=2.5,
                    label=style['label'], color=style['color'], markersize=7)
            ax.fill(angles, values, alpha=0.15, color=style['color'])

        # Fix axis to go clockwise and start at top
        ax.set_theta_offset(np.pi / 2)
        ax.set_theta_direction(-1)

        # Set category labels
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(categories, fontsize=11, fontweight='bold')

        # Set y-axis limits and labels
        ax.set_ylim(0, 100)
        ax.set_yticks([20, 40, 60, 80, 100])
        ax.set_yticklabels(['20%', '40%', '60%', '80%', '100%'], fontsize=9)

        # Add grid
        ax.grid(True, alpha=0.3, linestyle='--', linewidth=1)

        # Add title for each subplot
        ax.set_title(metric_title, fontsize=14, fontweight='bold', pad=20)

        # Add legend only to the last subplot
        if idx == 2:
            ax.legend(loc='upper left', bbox_to_anchor=(1.2, 1.1), fontsize=11, framealpha=0.95)

    # Add main title
    fig.suptitle('Tibetan MMLU: Model Performance Across 5 Categories\n(Concern All Answer Method, 0-shot Evaluation)',
                 fontsize=18, fontweight='bold', y=1.02)

    plt.tight_layout()

    # Save figure
    output_path = "../model_answer/concern_all_answer_combined_radar_chart.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✓ Saved combined chart: {output_path}")
    plt.close()

def main():
    """Generate all radar charts"""
    print("=" * 70)
    print("Generating Radar Charts for Tibetan MMLU Evaluation")
    print("=" * 70)
    print()

    # Create combined radar chart with all 3 metrics
    print("Creating combined radar chart (all 3 metrics)...")
    create_combined_radar_chart()
    print()

    # Create individual radar charts
    print("Creating individual radar charts...")

    charts = [
        ('Response Rate Average',
         'Response Rate Across 5 Categories\n(Concern All Answer Method, 0-shot)',
         'concern_all_answer_response_rate_radar_chart.png'),
        ('Conditional Accuracy Average',
         'Conditional Accuracy Across 5 Categories\n(Concern All Answer Method, 0-shot)',
         'concern_all_answer_conditional_accuracy_radar_chart.png'),
        ('Accuracy Average',
         'Overall Accuracy Across 5 Categories\n(Concern All Answer Method, 0-shot)',
         'concern_all_answer_accuracy_radar_chart.png')
    ]

    for metric_column, title, output_filename in charts:
        print(f"  - {metric_column}...")
        create_radar_chart(metric_column, title, output_filename)

    print()
    print("=" * 70)
    print("✓ All radar charts generated successfully!")
    print("Charts saved in: ../model_answer/")
    print("=" * 70)

if __name__ == "__main__":
    main()
