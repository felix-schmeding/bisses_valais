import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import pandas as pd

def plot_point_data(ax, profile_df, type_df, num_bins=20):
    # Create bins
    dist_min, dist_max = profile_df['dist_m'].min(), profile_df['dist_m'].max()
    bins = np.linspace(dist_min, dist_max, num_bins + 1)
    bin_centers = (bins[:-1] + bins[1:]) / 2
    bin_labels = list(range(num_bins))

    # Bin the data
    type_df = type_df.copy()
    type_df['bin'] = pd.cut(type_df['dist_m'], bins=bins, labels=False, include_lowest=True)

    # Count types per bin
    counts = type_df.groupby(['bin', 'type']).size().unstack(fill_value=0)
    counts = counts.reindex(index=bin_labels, fill_value=0)  # Fill missing bins

    # Colors
    types = counts.columns
    colors = plt.get_cmap("tab10")
    type_colors = {t: colors(i % 10) for i, t in enumerate(types)}

    # Stacked bar chart
    bottoms = np.zeros(len(counts))
    for t in types:
        values = counts[t].values
        ax.bar(bin_centers, values, bottom=bottoms, width=(bins[1] - bins[0]),
                label=t, color=type_colors[t], edgecolor='black')
        bottoms += values

    #ax2.bar(valid_centers, heights, width=(bins[1] - bins[0]), color=colors_used, edgecolor='black')
    ax.set_ylabel("Count")
    #
    ax.grid(True)

    # Legend
    ax.legend(title="Type", bbox_to_anchor=(1.01, 1), loc='upper left')

# --- Elevation Profile ---
def plot_elevation(ax, profile_df):
    
    ax.plot(profile_df['dist_m'], profile_df['elevation'], label="Elevation", color="black")

    ax.set_xlim(profile_df['dist_m'].min(), profile_df['dist_m'].max())
    ax.set_ylim(profile_df['elevation'].min(), profile_df['elevation'].max()+5)

    ax.set_ylabel("Elevation [m]")
    ax.set_title("Elevation Profile with Sections")
    ax.grid(True)

def plot_sections(ax, profile_df, sections_df, colors=None):

    if colors is None:
        # Auto-assign colors for categories
        unique_vals = sections_df['value'].unique()
        cmap = plt.get_cmap("tab10")
        colors = {val: cmap(i) for i, val in enumerate(unique_vals)}

    # --- Section Bars (bottom) ---
    for _, row in sections_df.iterrows():
        ax.add_patch(
            patches.Rectangle(
                (row['start_dist_m'], 0),  # (x, y)
                row['end_dist_m'] - row['start_dist_m'],  # width
                1,  # height
                color=colors[row['value']],
                label=row['value']
            )
        )

        # also works if 'sous_terre' column doesn't exist
        if row.get('sous_terre', False):    # return 'sous_terre' or false
            x = row['start_dist_m']
            width = row['end_dist_m'] - row['start_dist_m']
            ax.add_patch(
                patches.Rectangle(
                    (x, 0),
                    width,
                    1,
                    facecolor='none',     # No fill
                    edgecolor='black',
                    hatch='////',         # Choose hatch style
                    linewidth=0.0         # No visible edge, just hatch
                )
            )

    # Remove y-axis on bar chart
    ax.set_yticks([])
    #ax.set_xlabel("Distance [m]")
    ax.set_xlim(profile_df['dist_m'].min(), profile_df['dist_m'].max())

    # Add a legend for categories (avoid duplicates)
    handles = []
    labels_seen = set()
    for val, color in colors.items():
        if val not in labels_seen:
            handles.append(patches.Patch(color=color, label=val))
            labels_seen.add(val)
    ax.legend(handles=handles, loc='center left', bbox_to_anchor=(1.01, 0.5))


def plot_irrigated_area(ax, profile_df, valves_df, col_to_plot='total_area_' , num_bins=20):
    """
    Plot stacked irrigated area per crop type along a profile.

    Parameters:
        ax : matplotlib axis
        profile_df : DataFrame with 'dist_m' (used for bin range)
        valves_df : GeoDataFrame with 'dist_m' and 'total_area_{crop}' columns
        num_bins : Number of bins along the distance axis
    """

    # Step 1: Get all crop area columns (assumes prefix 'total_area_')
    area_cols = [col for col in valves_df.columns if col.startswith(col_to_plot)]
    crop_types = [col.replace(col_to_plot, '') for col in area_cols]

    # Step 2: Create distance bins
    dist_min, dist_max = profile_df['dist_m'].min(), profile_df['dist_m'].max()
    bins = np.linspace(dist_min, dist_max, num_bins + 1)
    bin_centers = (bins[:-1] + bins[1:]) / 2
    bin_labels = list(range(num_bins))

    # Step 3: Bin valves by dist_m
    valves_df = valves_df.copy()
    valves_df['bin'] = pd.cut(valves_df['dist_m'], bins=bins, labels=False, include_lowest=True)

    # Step 4: Sum area per bin and crop
    grouped = valves_df.groupby('bin')[area_cols].sum()
    grouped = grouped.reindex(index=bin_labels, fill_value=0)

    # Step 5: Prepare colors
    cmap = plt.get_cmap("tab10")
    colors = {crop: cmap(i % 10) for i, crop in enumerate(crop_types)}

    # Step 6: Plot stacked bars
    bottoms = np.zeros(len(grouped))
    for crop, col in zip(crop_types, area_cols):
        values = pd.to_numeric(grouped[col], errors='coerce').fillna(0).astype(float).values
        ax.bar(bin_centers, values, bottom=bottoms, width=(bins[1] - bins[0]),
               label=crop, color=colors[crop], edgecolor='black')
        bottoms += values

    ax.grid(True)

    # Legend
    ax.legend(title="Culture", bbox_to_anchor=(1.01, 1), loc='upper left')

