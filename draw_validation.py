import pandas as pd
import logging
import matplotlib.pyplot as plt
import constants as config

# Setup basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_validated_df():
    path = f'{config.RESULTS_DIR}/validated.csv'
    # Read space-separated CSV
    df = pd.read_csv(path, sep=' ')
    
    # Calculate % difference: (Prediction - Actual) / Actual * 100
    df['diff_pct'] = ((df['perf'] - df['actual_perf']) / df['actual_perf']) * 100
    
    # Create a combined label: "App vs Competitor"
    df['label'] = df['app'] + " vs " + df['competitor']
    return df

def draw_single_validation_chart(df):
    
    # Sort by error value for better visualization (optional, but recommended)
    df_sorted = df.sort_values(by='diff_pct')
    
    # Color coding: Green for over-prediction, Red for under-prediction
    colors = ['#2ecc71' if x >= 0 else '#e74c3c' for x in df_sorted['diff_pct']]

    max_per_chart = 16

    for i in range(0, len(df_sorted), max_per_chart):
        chunk = df_sorted.iloc[i:i + max_per_chart]


        n = len(chunk)
        # Adjust figure height dynamically based on the number of entries
        fig_height = max(10, n * 0.4) 
        plt.figure(figsize=(12, fig_height))

        # plt.figure(figsize=(10, 5))

        bars = plt.bar(
            chunk['label'],
            chunk['diff_pct'],
            color=colors[i:i + len(chunk)],
            alpha=0.8,
            edgecolor='black',
            linewidth=0.5
        )

        plt.ylabel("Performance Error (%)", fontsize=12, fontweight='bold')
        plt.title(f"Prediction Error (part {i//max_per_chart + 1})", fontsize=14, fontweight='bold', pad=20)

        plt.axhline(0, color='black', linewidth=1)

        # Rotate labels
        plt.xticks(rotation=35, ha='right')

        margin = max(abs(chunk['diff_pct'])) * 0.1
        plt.ylim(
            chunk['diff_pct'].min() - margin,
            chunk['diff_pct'].max() + margin
        )

        margin *= 0.1
        
        # Add labels
        for bar in bars:
            height = bar.get_height()
            plt.text(
                bar.get_x() + bar.get_width()/2,
                height + (margin if height >= 0 else -margin),
                f'{height:.2f}%',
                ha='center',
                va='bottom' if height >= 0 else 'top',
                fontsize=9
            )

        plt.tight_layout()
        
        output_path = f"{config.RESULTS_DIR}//all_validation_results{i}.png"
        plt.savefig(output_path, dpi=300)
        plt.close()
    
    # logger.info(f"Generated combined chart with {n} entries at {output_path}")

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