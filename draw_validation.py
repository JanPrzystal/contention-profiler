import pandas as pd
import logging
import matplotlib.pyplot as plt
import constants

# Setup basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_validated_df():
    path = f'{constants.RESULTS_DIR}/validated.csv'
    # Read space-separated CSV
    df = pd.read_csv(path, sep=',')
    
    # Calculate % difference: (Prediction - Actual) / Actual * 100
    df['diff_pct'] = ((df['perf'] - df['actual_perf']) / df['actual_perf']) * 100
    
    # Create a combined label: "App vs Competitor"
    df['label'] = df['app'] + " vs " + df['competitor']
    return df

def draw_single_validation_chart(df):
    n = len(df)
    # Adjust figure height dynamically based on the number of entries
    fig_height = max(10, n * 0.4) 
    plt.figure(figsize=(12, fig_height))
    
    # Sort by error value for better visualization (optional, but recommended)
    df_sorted = df.sort_values(by='diff_pct')
    
    # Color coding: Green for over-prediction, Red for under-prediction
    colors = ['#2ecc71' if x >= 0 else '#e74c3c' for x in df_sorted['diff_pct']]
    
    # Plot horizontal bars
    bars = plt.barh(df_sorted['label'], df_sorted['diff_pct'], color=colors, alpha=0.8, edgecolor='black', linewidth=0.5)
    
    # Formatting
    plt.axvline(0, color='black', linewidth=1) # Zero line
    plt.xlabel("Performance Error (%)", fontsize=12, fontweight='bold')
    plt.title("Prediction Error by Application Pair", fontsize=14, fontweight='bold', pad=20)
    plt.grid(axis='x', linestyle='--', alpha=0.7)
    
    # Add text labels at the end of each bar
    for bar in bars:
        width = bar.get_width()
        label_x_pos = width + (1 if width >= 0 else -1)
        plt.text(label_x_pos, bar.get_y() + bar.get_height()/2, 
                 f'{width:.2f}%', 
                 va='center', 
                 ha='left' if width >= 0 else 'right',
                 fontsize=9)

    # Adjust layout to prevent label clipping
    plt.tight_layout()
    
    output_path = f"{constants.RESULTS_DIR}//all_validation_results.png"
    plt.savefig(output_path, dpi=300)
    plt.close()
    
    logger.info(f"Generated combined chart with {n} entries at {output_path}")

def draw_validation():
    try:
        df = get_validated_df()
        
        # Log global stats
        max_err = df['diff_pct'].abs().max()
        avg_err = df['diff_pct'].abs().mean()
        logger.info(f"Global Max Error: {max_err:.2f}%")
        logger.info(f"Global Avg Error: {avg_err:.2f}%")

        draw_single_validation_chart(df)
        
    except Exception as e:
        logger.error(f"Failed to generate chart: {e}")

if __name__ == '__main__':
    draw_validation()