from typing import List

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

def get_validated_df(remove_cactu: bool = False, path: str = "") -> pd.DataFrame:
    if not path:
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

    # Filter out the app called 'cactu'
    if remove_cactu:
        df = df[df['app'] != 'cactu']

    # Create a combined label: "App vs Competitor"
    df['label'] = df['app'] + " vs " + df['competitor']
    df['ncompetitors'] = df['competitor'].apply(lambda x: len(x.split(" + ")))

    df['name'] = path.split("/")[-1]
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
        ax.set_xticklabels(chunk['label'], rotation=15, ha='right', fontsize=8)

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


def draw_errors_by_competitors(dfs: List[pd.DataFrame]) -> None:
    
    y_min = 0
    y_max = 0

    for df in dfs:
        if df['diff_pct'].min() < y_min:
            y_min = df['diff_pct'].min()
        if df['diff_pct'].max() > y_max:
            y_max = df['diff_pct'].max()

    y_padding = max((y_max - y_min) * 0.05, 0.1)

    for df in dfs:
        df['label'] = df['label'].filter

        plt.figure(figsize=(10, 6))

        # 2. Create the scatter plot
        # alpha=0.5 handles the overlapping points (density)
        plt.scatter(df['ncompetitors'], df['diff_pct'], alpha=0.5, label='Data Points')

        # 3. Calculate the trendline (Linear Regression)
        # We need to convert to numpy arrays to perform math
        x = df['ncompetitors'].values
        y = df['diff_pct'].values

        # polyfit returns coefficients [slope, intercept] for a 1st degree polynomial
        slope, intercept = np.polyfit(x, y, 1)

        # Create the line based on the slope and intercept
        trendline = slope * x + intercept

        # 4. Plot the trendline
        plt.plot(x, trendline, color='red', linewidth=2, label=f'Trend (slope: {slope:.2f})')

        # Set plot y-scale from the global diff_pct min/max across all dataframes
        plt.ylim(y_min - y_padding, y_max + y_padding)

        # 5. Formatting
        plt.title('Application Performance Error vs. Competitors', fontsize=14)
        plt.xlabel('Number of Competitors')
        plt.ylabel('Error (diff_pct %)')
        plt.legend() # Shows the labels we defined in scatter/plot
        plt.grid(True, linestyle='--', alpha=0.6)

        output_path = f"{config.RESULTS_DIR}//errors_by_competitors_{df['name'][0]}.png"
        plt.savefig(output_path, dpi=300)

if __name__ == '__main__':
    if len(sys.argv) > 1:
        dfs = []
        for path in sys.argv[1:]:
            dfs.append(get_validated_df(True, path))

        draw_errors_by_competitors(dfs)

    else:
        draw_validation()
