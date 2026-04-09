import pandas as pd
import logging
import matplotlib.pyplot as plt
import numpy as np
import config

# Setup basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_validated_df():
    path = f'{config.RESULTS_DIR}/validated.csv'
    # Read space-separated CSV
    df = pd.read_csv(path, sep=',')
    
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

    max_per_chart = 12

    for i in range(0, len(df_sorted), max_per_chart):
        chunk = df_sorted.iloc[i:i + max_per_chart]


        n = len(chunk)
        x = np.arange(n)
        width = 0.35
        # Adjust figure height dynamically based on the number of entries
        fig_height = max(10, n * 0.4) 
        fig, ax1 = plt.subplots(figsize=(12, fig_height))
        ax2 = ax1.twinx()

        bars1 = ax1.bar(
            x - width/2,
            chunk['diff_pct'],
            width,
            color='#e74c3c', #colors[i:i + len(chunk)],
            alpha=0.8,
            edgecolor='black',
            linewidth=0.5,
            label='Performance Error (%)'
        )

        bars2 = ax2.bar(
            x + width/2,
            chunk['contentiousness'],
            width,
            color='#3498db',
            alpha=0.8,
            edgecolor='black',
            linewidth=0.5,
            label='Contentiousness'
        )

        ax1.set_ylabel("Performance Error (%)", fontsize=12, fontweight='bold')
        ax2.set_ylabel("Contentiousness (MB)", fontsize=12, fontweight='bold')
        ax1.set_title(f"Prediction Error (part {i//max_per_chart + 1})", fontsize=14, fontweight='bold', pad=20)
        ax1.legend(loc='upper left')
        ax2.legend(loc='upper right')

        ax1.axhline(0, color='black', linewidth=1)

        ax1.set_xticks(x)
        ax1.set_xticklabels(chunk['label'], rotation=35, ha='right')

        # Set ylim for each axis to align 0 at the same position
        margin1 = abs(chunk['diff_pct']).max() * 0.1
        margin2 = abs(chunk['contentiousness']).max() * 0.1
        bottom = min(chunk['diff_pct'].min() - margin1, chunk['contentiousness'].min() - margin2)
        top1 = chunk['diff_pct'].max() + margin1
        top2 = chunk['contentiousness'].max() + margin2
        range_ax1 = top1 - bottom
        range_ax2 = top2 - bottom
        max_range = max(range_ax1, range_ax2)
        ax1.set_ylim(bottom, bottom + max_range)
        ax2.set_ylim(bottom, bottom + max_range)

        margin1 *= 0.1
        
        # Add labels for the first bars (error %)
        for bar in bars1:
            height = bar.get_height()
            ax1.text(
                bar.get_x() + bar.get_width()/2,
                height + (margin1 if height >= 0 else -margin1),
                f'{height:.2f}%',
                ha='center',
                va='bottom' if height >= 0 else 'top',
                fontsize=9
            )

        fig.tight_layout()
        
        output_path = f"{config.RESULTS_DIR}//all_validation_results{i}.png"
        fig.savefig(output_path, dpi=300)
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