"""
presentation_dashboard.py

Generate comprehensive visualization dashboard for mentor presentation.
Includes:
  - Confusion matrix heatmap (Track A)
  - R² score comparison (Track B)
  - Per-grade performance breakdown
  - Feature importance bar chart
  - Architecture diagram (text-based)
  - Performance summary table
"""

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.patches import Rectangle
import json
import os

# Set style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")


def plot_confusion_matrix_track_a():
    """
    Generate confusion matrix heatmap for Track A classification.
    Shows Grade A/B/C/D predictions vs actual.
    """
    # Confusion matrix from training results
    cm = np.array([
        [62, 23,  0,  2],
        [25, 79, 12,  2],
        [ 1,  8, 72, 10],
        [ 0,  3, 13, 98]
    ])
    
    grades = ['A\n(0-3 days)', 'B\n(4-7 days)', 'C\n(8-10 days)', 'D\n(>10 days)']
    
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # Create heatmap
    sns.heatmap(cm, annot=True, fmt='d', cmap='YlGnBu', 
                xticklabels=grades, yticklabels=grades,
                cbar_kws={'label': 'Count'}, ax=ax,
                linewidths=2, linecolor='white')
    
    ax.set_title('Track A: Confusion Matrix - Freshness Grade Classification\n(Test Set: 410 samples)', 
                 fontsize=14, fontweight='bold', pad=20)
    ax.set_ylabel('Actual Grade', fontsize=12, fontweight='bold')
    ax.set_xlabel('Predicted Grade', fontsize=12, fontweight='bold')
    
    # Add diagonal accuracy highlight
    for i in range(4):
        rect = Rectangle((i, i), 1, 1, fill=False, edgecolor='red', lw=3)
        ax.add_patch(rect)
    
    plt.tight_layout()
    plt.savefig('presentation_assets/01_confusion_matrix.png', dpi=300, bbox_inches='tight')
    print("✓ Saved: 01_confusion_matrix.png")
    plt.close()


def plot_per_grade_performance():
    """
    Bar chart showing precision, recall, F1 per grade.
    """
    grades = ['A\nPremium', 'B\nGood', 'C\nFair', 'D\nPoor']
    precision = [0.70, 0.70, 0.74, 0.88]
    recall = [0.71, 0.67, 0.79, 0.86]
    f1 = [0.71, 0.68, 0.77, 0.87]
    
    x = np.arange(len(grades))
    width = 0.25
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    ax.bar(x - width, precision, width, label='Precision', color='#FF6B6B', alpha=0.8)
    ax.bar(x, recall, width, label='Recall', color='#4ECDC4', alpha=0.8)
    ax.bar(x + width, f1, width, label='F1-Score', color='#45B7D1', alpha=0.8)
    
    ax.set_ylabel('Score', fontsize=12, fontweight='bold')
    ax.set_title('Track A: Per-Grade Performance Metrics\n(Precision, Recall, F1-Score)', 
                 fontsize=14, fontweight='bold', pad=20)
    ax.set_xticks(x)
    ax.set_xticklabels(grades, fontsize=11)
    ax.legend(fontsize=11, loc='lower right')
    ax.set_ylim([0, 1.0])
    ax.grid(axis='y', alpha=0.3)
    
    # Add value labels on bars
    for bars in [ax.bar(x - width, precision, width), 
                 ax.bar(x, recall, width), 
                 ax.bar(x + width, f1, width)]:
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.2f}', ha='center', va='bottom', fontsize=9)
    
    plt.tight_layout()
    plt.savefig('presentation_assets/02_per_grade_performance.png', dpi=300, bbox_inches='tight')
    print("✓ Saved: 02_per_grade_performance.png")
    plt.close()


def plot_regression_metrics():
    """
    Comparison of Track B regression model metrics.
    """
    models = ['Storage Day\nPrediction', 'Folic Acid\nPrediction']
    r2_scores = [0.837, 0.9997]
    rmse = [1.65, 0.79]
    mae = [1.14, 0.73]
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # R² Score comparison
    colors_r2 = ['#FF6B6B', '#4ECDC4']
    bars1 = ax1.bar(models, r2_scores, color=colors_r2, alpha=0.8, edgecolor='black', linewidth=2)
    ax1.set_ylabel('R² Score', fontsize=12, fontweight='bold')
    ax1.set_title('Track B: Model Fit Quality (R² Score)\nHigher is better (max=1.0)', 
                  fontsize=12, fontweight='bold', pad=15)
    ax1.set_ylim([0, 1.05])
    ax1.axhline(y=0.8, color='green', linestyle='--', linewidth=2, label='Good threshold (0.8)', alpha=0.7)
    ax1.legend(fontsize=10)
    ax1.grid(axis='y', alpha=0.3)
    
    for i, (bar, val) in enumerate(zip(bars1, r2_scores)):
        ax1.text(bar.get_x() + bar.get_width()/2., val + 0.02,
                f'{val:.4f}', ha='center', va='bottom', fontsize=11, fontweight='bold')
    
    # RMSE & MAE comparison
    x = np.arange(len(models))
    width = 0.35
    
    bars2_1 = ax2.bar(x - width/2, rmse, width, label='RMSE', color='#FF6B6B', alpha=0.8)
    bars2_2 = ax2.bar(x + width/2, mae, width, label='MAE', color='#45B7D1', alpha=0.8)
    
    ax2.set_ylabel('Error (Units)', fontsize=12, fontweight='bold')
    ax2.set_title('Track B: Prediction Error\n(Lower is better)', 
                  fontsize=12, fontweight='bold', pad=15)
    ax2.set_xticks(x)
    ax2.set_xticklabels(['Days', 'µM'], fontsize=11)
    ax2.legend(fontsize=10)
    ax2.grid(axis='y', alpha=0.3)
    
    for bars in [bars2_1, bars2_2]:
        for bar in bars:
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.2f}', ha='center', va='bottom', fontsize=10)
    
    plt.tight_layout()
    plt.savefig('presentation_assets/03_regression_metrics.png', dpi=300, bbox_inches='tight')
    print("✓ Saved: 03_regression_metrics.png")
    plt.close()


def plot_feature_importance():
    """
    Top 5 selected features by importance (RFE + SHAP aligned).
    """
    features = ['DCT_3', 'DCT_2', 'Mean', 'Energy', 'DCT_1']
    importance = [0.22, 0.20, 0.18, 0.16, 0.15]  # Relative importance
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    colors = plt.cm.viridis(np.linspace(0.3, 0.9, len(features)))
    bars = ax.barh(features, importance, color=colors, edgecolor='black', linewidth=1.5)
    
    ax.set_xlabel('Relative Importance (RFE + SHAP aligned)', fontsize=12, fontweight='bold')
    ax.set_title('Top 5 Features Selected by RFE\n(From 11 engineered features)', 
                 fontsize=14, fontweight='bold', pad=20)
    ax.set_xlim([0, max(importance) * 1.15])
    ax.grid(axis='x', alpha=0.3)
    
    for bar, val in zip(bars, importance):
        ax.text(val + 0.01, bar.get_y() + bar.get_height()/2.,
               f'{val:.2f}', va='center', fontsize=11, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('presentation_assets/04_feature_importance.png', dpi=300, bbox_inches='tight')
    print("✓ Saved: 04_feature_importance.png")
    plt.close()


def plot_architecture_diagram():
    """
    Text-based architecture flow visualization.
    """
    fig, ax = plt.subplots(figsize=(14, 10))
    ax.axis('off')
    
    # Title
    ax.text(0.5, 0.95, 'Orange Freshness Detection - System Architecture', 
            ha='center', fontsize=16, fontweight='bold', transform=ax.transAxes)
    
    # Draw boxes and flow
    y_pos = 0.87
    
    # Input
    rect_input = Rectangle((0.15, y_pos - 0.05), 0.7, 0.05, 
                           fill=True, facecolor='#FFE5E5', edgecolor='black', linewidth=2,
                           transform=ax.transAxes)
    ax.add_patch(rect_input)
    ax.text(0.5, y_pos - 0.025, 'Raw Sensor Data (15 optical readings per orange)', 
            ha='center', va='center', fontsize=11, fontweight='bold', transform=ax.transAxes)
    
    # Arrow
    ax.annotate('', xy=(0.5, y_pos - 0.07), xytext=(0.5, y_pos - 0.05),
                arrowprops=dict(arrowstyle='->', lw=2), transform=ax.transAxes)
    
    y_pos -= 0.10
    
    # Preprocessing
    rect_preproc = Rectangle((0.1, y_pos - 0.08), 0.8, 0.08, 
                            fill=True, facecolor='#E5F5FF', edgecolor='#0066CC', linewidth=2,
                            transform=ax.transAxes)
    ax.add_patch(rect_preproc)
    preproc_text = 'PREPROCESSING: Savitzky-Golay (w=11, p=3) → DCT (10 coeff) → Energy\nOutput: 11 engineered features'
    ax.text(0.5, y_pos - 0.04, preproc_text, ha='center', va='center', 
            fontsize=10, transform=ax.transAxes)
    
    ax.annotate('', xy=(0.5, y_pos - 0.10), xytext=(0.5, y_pos - 0.08),
                arrowprops=dict(arrowstyle='->', lw=2), transform=ax.transAxes)
    
    y_pos -= 0.14
    
    # Feature Engineering
    rect_feat = Rectangle((0.1, y_pos - 0.06), 0.8, 0.06, 
                          fill=True, facecolor='#FFF5E5', edgecolor='#FF9900', linewidth=2,
                          transform=ax.transAxes)
    ax.add_patch(rect_feat)
    ax.text(0.5, y_pos - 0.03, 'StandardScaler + RFE (11 → 5 features) + Imputation', 
            ha='center', va='center', fontsize=10, fontweight='bold', transform=ax.transAxes)
    
    ax.annotate('', xy=(0.5, y_pos - 0.08), xytext=(0.5, y_pos - 0.06),
                arrowprops=dict(arrowstyle='->', lw=2), transform=ax.transAxes)
    
    y_pos -= 0.12
    
    # Split into two tracks
    ax.text(0.5, y_pos + 0.02, 'Two Parallel Prediction Tracks', ha='center', 
            fontsize=11, fontweight='bold', transform=ax.transAxes, style='italic')
    
    # Track B (left)
    ax.annotate('', xy=(0.25, y_pos - 0.02), xytext=(0.5, y_pos),
                arrowprops=dict(arrowstyle='->', lw=2), transform=ax.transAxes)
    
    # Track A (right)
    ax.annotate('', xy=(0.75, y_pos - 0.02), xytext=(0.5, y_pos),
                arrowprops=dict(arrowstyle='->', lw=2), transform=ax.transAxes)
    
    y_pos -= 0.10
    
    # Track B: Regression
    rect_trackb = Rectangle((0.05, y_pos - 0.12), 0.4, 0.12, 
                           fill=True, facecolor='#E5FFE5', edgecolor='#006600', linewidth=2,
                           transform=ax.transAxes)
    ax.add_patch(rect_trackb)
    trackb_text = 'TRACK B: REGRESSION\n\nDay Model (RF): R²=0.837\nFolic Acid Model (RF): R²=0.9997\n\nOutputs: Age (days), Folic (µM)'
    ax.text(0.25, y_pos - 0.06, trackb_text, ha='center', va='center', 
            fontsize=9.5, transform=ax.transAxes)
    
    # Track A: Classification
    rect_tracka = Rectangle((0.55, y_pos - 0.12), 0.4, 0.12, 
                           fill=True, facecolor='#FFE5FF', edgecolor='#9900FF', linewidth=2,
                           transform=ax.transAxes)
    ax.add_patch(rect_tracka)
    tracka_text = 'TRACK A: CLASSIFICATION\n\nStackingClassifier (RF+SVM)\nAccuracy: 75.85%\n\nOutputs: Grade (A/B/C/D) + Probs'
    ax.text(0.75, y_pos - 0.06, tracka_text, ha='center', va='center', 
            fontsize=9.5, transform=ax.transAxes)
    
    # Arrows to output
    ax.annotate('', xy=(0.25, y_pos - 0.15), xytext=(0.25, y_pos - 0.12),
                arrowprops=dict(arrowstyle='->', lw=2), transform=ax.transAxes)
    ax.annotate('', xy=(0.75, y_pos - 0.15), xytext=(0.75, y_pos - 0.12),
                arrowprops=dict(arrowstyle='->', lw=2), transform=ax.transAxes)
    
    y_pos -= 0.20
    
    # Final Output
    rect_output = Rectangle((0.1, y_pos - 0.08), 0.8, 0.08, 
                           fill=True, facecolor='#FFE5E5', edgecolor='black', linewidth=2,
                           transform=ax.transAxes)
    ax.add_patch(rect_output)
    output_text = 'UNIFIED OUTPUT: {age_days, folic_µM, grade, probabilities, remaining_days, confidence}'
    ax.text(0.5, y_pos - 0.04, output_text, ha='center', va='center', 
            fontsize=10, fontweight='bold', transform=ax.transAxes)
    
    # Add key features box
    y_pos -= 0.15
    ax.text(0.05, y_pos, 'KEY FEATURES:', fontsize=10, fontweight='bold', transform=ax.transAxes)
    features_text = '''✓ Modular design (4 independent Python modules)
✓ No data leakage (batch-wise train/test split)
✓ Proper imputation & scaling
✓ RFE-selected top 5 features
✓ SHAP-aligned interpretability
✓ End-to-end tested & verified'''
    ax.text(0.05, y_pos - 0.10, features_text, fontsize=9, transform=ax.transAxes,
            verticalalignment='top', family='monospace')
    
    plt.tight_layout()
    plt.savefig('presentation_assets/05_architecture_diagram.png', dpi=300, bbox_inches='tight')
    print("✓ Saved: 05_architecture_diagram.png")
    plt.close()


def plot_data_split_summary():
    """
    Shows training/test split breakdown for both tracks.
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 6))
    
    # Track B: Regression data split
    labels_b = ['Train\n(Batches 1-5)', 'Test\n(Batches 6-7)\nUnseen']
    sizes_b = [35, 15]
    colors_b = ['#4ECDC4', '#FF6B6B']
    
    ax1.pie(sizes_b, labels=labels_b, autopct='%1.1f%%', startangle=90,
            colors=colors_b, textprops={'fontsize': 11, 'fontweight': 'bold'},
            wedgeprops=dict(edgecolor='black', linewidth=2))
    ax1.set_title('Track B: Data Split (Storage Day Model)\n50 real samples\nBatch-wise split (NO leakage)', 
                  fontsize=12, fontweight='bold', pad=20)
    
    # Track A: Classification data split
    labels_a = ['Train\n(80%)', 'Test\n(20%)']
    sizes_a = [1640, 410]
    colors_a = ['#45B7D1', '#F7B731']
    
    ax2.pie(sizes_a, labels=labels_a, autopct='%1.1f%%', startangle=90,
            colors=colors_a, textprops={'fontsize': 11, 'fontweight': 'bold'},
            wedgeprops=dict(edgecolor='black', linewidth=2))
    ax2.set_title('Track A: Data Split (Grade Classification)\n2050 engineered features\nStratified split', 
                  fontsize=12, fontweight='bold', pad=20)
    
    plt.tight_layout()
    plt.savefig('presentation_assets/06_data_split_summary.png', dpi=300, bbox_inches='tight')
    print("✓ Saved: 06_data_split_summary.png")
    plt.close()


def generate_all_dashboards():
    """Generate all visualization assets."""
    os.makedirs('presentation_assets', exist_ok=True)
    
    print("\n" + "="*70)
    print("GENERATING PRESENTATION DASHBOARD")
    print("="*70)
    
    print("\n[1/6] Confusion Matrix...")
    plot_confusion_matrix_track_a()
    
    print("[2/6] Per-Grade Performance...")
    plot_per_grade_performance()
    
    print("[3/6] Regression Metrics...")
    plot_regression_metrics()
    
    print("[4/6] Feature Importance...")
    plot_feature_importance()
    
    print("[5/6] Architecture Diagram...")
    plot_architecture_diagram()
    
    print("[6/6] Data Split Summary...")
    plot_data_split_summary()
    
    print("\n" + "="*70)
    print("✅ ALL DASHBOARDS GENERATED")
    print("="*70)
    print("\nAssets saved to: presentation_assets/")
    print("  01_confusion_matrix.png")
    print("  02_per_grade_performance.png")
    print("  03_regression_metrics.png")
    print("  04_feature_importance.png")
    print("  05_architecture_diagram.png")
    print("  06_data_split_summary.png")


if __name__ == '__main__':
    generate_all_dashboards()
