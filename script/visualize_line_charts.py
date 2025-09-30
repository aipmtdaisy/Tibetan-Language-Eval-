#!/usr/bin/env python3
"""
Create line charts for Tibetan MMLU evaluation results
Compares all 4 models across 67 subjects using concern_all_answer metrics
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend

# Set style for better-looking plots
plt.style.use('seaborn-v0_8-darkgrid')
matplotlib.rcParams['font.family'] = 'DejaVu Sans'
matplotlib.rcParams['figure.figsize'] = (20, 8)

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

def create_line_chart(metric_name, metric_column, ylabel, output_filename):
    """Create a line chart comparing all 4 models for a specific metric"""

    models = {
        'gemini-2-5-pro': {'color': '#4285F4', 'marker': 'o', 'label': 'Gemini 2.5 Pro'},
        'gemini-2-5-flash': {'color': '#34A853', 'marker': 's', 'label': 'Gemini 2.5 Flash'},
        'claude-opus-4-1': {'color': '#EA4335', 'marker': '^', 'label': 'Claude Opus 4.1'},
        'claude-sonnet-4-5': {'color': '#FBBC04', 'marker': 'D', 'label': 'Claude Sonnet 4.5'}
    }

    fig, ax = plt.subplots(figsize=(24, 8))

    # Load data for first model to get subject names
    first_model = list(models.keys())[0]
    df_first = load_model_data(first_model)
    subjects = df_first['File Name'].tolist()

    # Plot each model
    for model_id, style in models.items():
        df = load_model_data(model_id)

        # Convert percentage strings to float
        values = df[metric_column].apply(clean_percentage).tolist()

        ax.plot(range(len(subjects)), values,
                marker=style['marker'],
                linewidth=2,
                markersize=6,
                label=style['label'],
                color=style['color'],
                alpha=0.8)

    # Customize the plot
    ax.set_xlabel('Subject', fontsize=14, fontweight='bold')
    ax.set_ylabel(ylabel, fontsize=14, fontweight='bold')
    ax.set_title(f'Model Performance Comparison - {metric_name}\n(Concern All Answer Method, 0-shot)',
                 fontsize=16, fontweight='bold', pad=20)

    # Set x-axis labels
    ax.set_xticks(range(len(subjects)))
    ax.set_xticklabels(subjects, rotation=90, ha='right', fontsize=8)

    # Set y-axis range
    ax.set_ylim(0, 105)
    ax.grid(True, alpha=0.3, linestyle='--')

    # Add legend
    ax.legend(fontsize=12, loc='upper right', framealpha=0.9)

    # Tight layout to prevent label cutoff
    plt.tight_layout()

    # Save the figure
    output_path = f"../model_answer/{output_filename}"
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✓ Saved: {output_path}")
    plt.close()

def create_combined_accuracy_chart():
    """Create a single chart showing accuracy for all models"""

    models = {
        'gemini-2-5-pro': {'color': '#4285F4', 'marker': 'o', 'label': 'Gemini 2.5 Pro'},
        'gemini-2-5-flash': {'color': '#34A853', 'marker': 's', 'label': 'Gemini 2.5 Flash'},
        'claude-opus-4-1': {'color': '#EA4335', 'marker': '^', 'label': 'Claude Opus 4.1'},
        'claude-sonnet-4-5': {'color': '#FBBC04', 'marker': 'D', 'label': 'Claude Sonnet 4.5'}
    }

    fig, ax = plt.subplots(figsize=(24, 10))

    # Load data for first model to get subject names
    first_model = list(models.keys())[0]
    df_first = load_model_data(first_model)
    subjects = df_first['File Name'].tolist()

    # Plot each model
    for model_id, style in models.items():
        df = load_model_data(model_id)

        # Convert percentage strings to float
        values = df['Accuracy'].apply(clean_percentage).tolist()

        ax.plot(range(len(subjects)), values,
                marker=style['marker'],
                linewidth=2.5,
                markersize=7,
                label=style['label'],
                color=style['color'],
                alpha=0.85)

    # Customize the plot
    ax.set_xlabel('Test Subject', fontsize=16, fontweight='bold')
    ax.set_ylabel('Accuracy (%)', fontsize=16, fontweight='bold')
    ax.set_title('Tibetan MMLU: Model Performance Comparison Across 67 Subjects\n(Concern All Answer Method, 0-shot Evaluation)',
                 fontsize=18, fontweight='bold', pad=25)

    # Set x-axis labels with better formatting
    ax.set_xticks(range(len(subjects)))
    # Format subject names: replace underscores with spaces and title case
    formatted_subjects = [s.replace('_', ' ').title() for s in subjects]
    ax.set_xticklabels(formatted_subjects, rotation=90, ha='right', fontsize=9)

    # Set y-axis range and ticks
    ax.set_ylim(0, 105)
    ax.set_yticks(range(0, 101, 10))
    ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.8)

    # Add horizontal line at 50% (random guessing for 4 choices = 25%, but 50% is reasonable performance)
    ax.axhline(y=25, color='gray', linestyle=':', linewidth=1.5, alpha=0.5, label='Random Baseline (25%)')

    # Add legend with better positioning
    ax.legend(fontsize=13, loc='upper left', framealpha=0.95, shadow=True)

    # Tight layout to prevent label cutoff
    plt.tight_layout()

    # Save the figure
    output_path = "../model_answer/concern_all_answer_accuracy_comparison_line_chart.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✓ Saved main chart: {output_path}")
    plt.close()

def main():
    """Generate all line charts"""
    print("=" * 70)
    print("Generating Line Charts for Tibetan MMLU Evaluation")
    print("=" * 70)
    print()

    # Create main accuracy comparison chart
    print("Creating main accuracy comparison chart...")
    create_combined_accuracy_chart()
    print()

    # Create individual metric charts
    print("Creating individual metric charts...")

    metrics = [
        ('Response Rate', 'Response Rate', 'Response Rate (%)', 'concern_all_answer_response_rate_line_chart.png'),
        ('Conditional Accuracy', 'Conditional Accuracy', 'Conditional Accuracy (%)', 'concern_all_answer_conditional_accuracy_line_chart.png'),
        ('Accuracy', 'Accuracy', 'Accuracy (%)', 'concern_all_answer_accuracy_line_chart.png')
    ]

    for metric_name, metric_column, ylabel, output_filename in metrics:
        print(f"  - {metric_name}...")
        create_line_chart(metric_name, metric_column, ylabel, output_filename)

    print()
    print("=" * 70)
    print("✓ All line charts generated successfully!")
    print("Charts saved in: ../model_answer/")
    print("=" * 70)

if __name__ == "__main__":
    main()
