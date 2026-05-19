import pandas as pd
import logging
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import MaxNLocator

import sys
from pathlib import Path
parent_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(parent_dir))
import config

# Setup basic logging
from experiment_setup.log import log

def get_validated_df():
    path = f'{config.RESULTS_DIR}/validated.csv'
    # Read space-separated CSV
    df = pd.read_csv(path, sep=',')
    
    # Calculate % difference: (Prediction - Actual) / Actual * 100
    df['diff_pct'] = ((df['perf'] - df['actual_perf']) / df['actual_perf']) * 100
    
    # Shorten the application names
    df["competitor"] = df["competitor"].apply(
        lambda s: " + ".join(name.split(".")[1].split("_")[0][:5] for name in s.split(" + "))
    )
    df['app'] = df['app'].apply(
        lambda s: s.split(".")[1].split("_")[0][:5]
    )

    # Create a combined label: "App vs Competitor"
    df['label'] = df['app'] + " vs " + df['competitor']
    df['ncompetitors'] = df['competitor'].apply(lambda x: len(x.split(" + ")))
    return df

def draw_single_validation_chart(df):
    
    # Sort by error value for better visualization (optional, but recommended)
    df_sorted = df.sort_values(by='diff_pct')
    
    max_per_chart = 12

    for i in range(0, len(df_sorted), max_per_chart):
        chunk = df_sorted.iloc[i:i + max_per_chart]

        n = len(chunk)
        x = np.arange(n)

        fig = plt.figure(figsize=(14, max(8, n * 0.7)))
        ax = fig.add_subplot(111, projection='3d')

        # Use color to encode contentiousness, while y is performance error and z is number of competitors.
        scatter = ax.scatter(
            x,
            chunk['diff_pct'],
            chunk['ncompetitors'],
            c=chunk['contentiousness'],
            cmap='viridis',
            s=80,
            edgecolor='k',
            alpha=0.9
        )

        # ax.set_xlabel("Entry", fontsize=12, fontweight='bold')
        ax.set_ylabel("Prediction Error (%)", fontsize=12, fontweight='bold')
        ax.set_zlabel("Number of Competitors", fontsize=12, fontweight='bold')
        ax.set_title(f"Prediction Validation (part {i//max_per_chart + 1})", fontsize=14, fontweight='bold', pad=20)

        ax.set_xticks(x)
        ax.set_xticklabels(chunk['label'], rotation=35, ha='right', fontsize=8)

        min_comp = int(chunk['ncompetitors'].min())
        max_comp = int(chunk['ncompetitors'].max())
        if min_comp == max_comp:
            max_comp += 1
        ax.set_zticks(np.arange(min_comp, max_comp + 1, 1))
        ax.zaxis.set_major_locator(MaxNLocator(integer=True))

        ax.view_init(elev=25, azim=-60)

        cbar = fig.colorbar(scatter, ax=ax, pad=0.15)
        cbar.set_label('Contentiousness (MB)', fontsize=11, fontweight='bold')

        # Annotate each point with its error percentage and competitor count
        for xi, yi, zi in zip(x, chunk['diff_pct'], chunk['ncompetitors']):
            ax.text(xi, yi, zi, f'{yi:.1f}% / {zi}', fontsize=8, ha='center', va='bottom')

        fig.tight_layout()
        
        output_path = f"{config.RESULTS_DIR}//all_validation_results{i}.png"
        fig.savefig(output_path, dpi=300)
        plt.close()
    
    # log(f"Generated combined chart with {n} entries at {output_path}")

def draw_validation():
    try:
        df = get_validated_df()
        
        # Log global stats
        max_err = df['diff_pct'].abs().max()
        avg_err = df['diff_pct'].abs().mean()
        log(f"Global Max Error: {max_err:.2f}%")
        log(f"Global Avg Error: {avg_err:.2f}%")

        draw_single_validation_chart(df)
        
    except Exception as e:
        log(f"Failed to generate chart: {e}", level=logging.ERROR)

if __name__ == '__main__':
    draw_validation()