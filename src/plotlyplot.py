import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import pandas as pd

general_config = {
    "staticPlot": False,  # Make the plot interactive
    "displayModeBar": False,  # Hide the mode bar
    "scrollZoom": False,  # Disable zooming with the scroll wheel
    "doubleClick": False,  # Disable resetting the view on double-click
    "displaylogo": False,  # Hide the Plotly logo
}


def plot_sections(fig, df, range_el, fig_height=200):

    # need to set fig title and ax limits outsite with info of json file

    unique_vals = df["value"].unique()
    # cmap = plt.get_cmap("tab10")
    cmap = px.colors.qualitative.G10
    # colors = {val: to_hex(cmap(i)) for i, val in enumerate(unique_vals)}
    colors = {val: cmap[i % len(cmap)] for i, val in enumerate(unique_vals)}

    already_legend = []

    # Create a column for the length of each segment needed to plot
    df["length"] = df["end_dist_m"] - df["start_dist_m"]

    for index, sec in df.iterrows():
        leg = False
        if sec["value"] not in already_legend:
            already_legend.append(sec["value"])
            leg = True
        fig.add_trace(
            go.Bar(
                x=[sec["length"]],
                y=["    "],  # Use a single space as y-tick label instead of 0
                orientation="h",
                marker=dict(
                    color=colors[sec["value"]],
                    line=dict(color="rgb(0,0,0)", width=0),
                ),
                # marker_color = ,
                name=sec["value"],
                showlegend=leg,
            )
        )

    fig.update_layout(
        # title="Section",
        xaxis=dict(
            showgrid=False,
            showline=True,
            showticklabels=True,
            zeroline=False,
            # domain=[0, 0.8],
            range=[range_el[0], range_el[1]],
            automargin=True,
        ),
        yaxis=dict(
            title=" ",
            showgrid=False,
            showline=False,
            showticklabels=True,  # Show y-tick labels
            # tickvals=[0],  # Only show tick at 0
            # ticktext=[" "],  # Replace label 0 with a space
            zeroline=False,
            # range=[-0.1, 0.1],
            # automargin=True,
        ),
        # barmode="stack",  # makes it a stacked graph
        barmode="relative",  # makes it a stacked graph
        # paper_bgcolor="rgb(248, 248, 255)",
        # plot_bgcolor="rgb(248, 248, 255)",
        # margin=dict(l=120, r=10, t=140, b=80),
        showlegend=True,
        legend=dict(
            itemclick=False,  # Disable click interactions in the legend
            itemdoubleclick=False,  # Disable double-click interactions in the legend
        ),
        height=fig_height,
        dragmode=False,
        margin=dict(l=20, r=0, t=0, b=0),
    )

    fig.update_traces(marker_line_width=0, width=0.5)


def plot_point_data(fig, type_df, range_el, fig_height=200, num_bins=20):
    """
    Plot point data as a stacked bar chart using Plotly.

    Parameters:
        profile_df : DataFrame with 'dist_m' (distance) column
        type_df : DataFrame with 'dist_m' (distance) and 'type' columns
        num_bins : Number of bins along the distance axis
    """
    # Create bins
    # dist_min, dist_max = profile_df["dist_m"].min(), profile_df["dist_m"].max()
    bins = np.linspace(range_el[0], range_el[1], num_bins + 1)
    bin_centers = (bins[:-1] + bins[1:]) / 2
    bin_labels = list(range(num_bins))

    # Bin the data
    type_df = type_df.copy()
    type_df["bin"] = pd.cut(
        type_df["dist_m"], bins=bins, labels=False, include_lowest=True
    )

    # Count types per bin
    counts = type_df.groupby(["bin", "type"]).size().unstack(fill_value=0)
    counts = counts.reindex(index=bin_labels, fill_value=0)  # Fill missing bins

    # Colors
    types = counts.columns
    colors = px.colors.qualitative.Set3  # Use a Plotly color palette
    type_colors = {t: colors[i % len(colors)] for i, t in enumerate(types)}

    # Create the figure
    # fig = go.Figure()

    # Stacked bar chart
    bottoms = np.zeros(len(counts))
    for t in types:
        values = counts[t].values
        fig.add_trace(
            go.Bar(
                x=bin_centers,
                y=values,
                name=t,
                marker=dict(color=type_colors[t]),
            )
        )
        bottoms += values

    # Update layout
    fig.update_layout(
        barmode="stack",
        # title="Point Data Distribution",
        xaxis=dict(
            title="Distance [m]",
            range=[range_el[0], range_el[1]],
            showgrid=True,
        ),
        yaxis=dict(
            title="Count",
            showgrid=True,
        ),
        legend=dict(
            itemclick=False,  # Disable click interactions in the legend
            itemdoubleclick=False,  # Disable double-click interactions in the legend
        ),
        template="plotly_white",
        height=fig_height,
        margin=dict(l=0, r=0, t=0, b=0),
    )

    # fig.update_yaxes(automargin=True)

    # Show the plot
    # fig.show()


def plot_surface_data(
    fig, type_df, range_el, col=["type", "value"], fig_height=200, num_bins=20
):
    """
    Plot point data as a stacked bar chart using Plotly.

    Parameters:
        profile_df : DataFrame with 'dist_m' column (full profile distances)
        type_df    : DataFrame with 'dist_m' and 'type' columns (point data)
        col        : List with two elements, first is the column for type, second is the column for value
        num_bins   : Number of bins to aggregate into
    """
    # Define bin edges using full profile extent
    bins = np.linspace(range_el[0], range_el[1], num_bins + 1)
    bin_centers = (bins[:-1] + bins[1:]) / 2
    bin_labels = list(range(num_bins))

    # Bin point data into these bins
    type_df = type_df.copy()
    type_df["bin"] = pd.cut(
        type_df["dist_m"], bins=bins, labels=False, include_lowest=True
    )

    # Count occurrences of each type per bin
    # counts = type_df.groupby(["bin", "type"]).size().unstack(fill_value=0)
    counts = type_df.groupby(["bin", col[0]])[col[1]].sum().unstack(fill_value=0)
    counts = counts.reindex(
        index=bin_labels, fill_value=0
    )  # Ensure all bins are included

    # Assign colors
    types = counts.columns
    colors = px.colors.qualitative.Set3
    type_colors = {t: colors[i % len(colors)] for i, t in enumerate(types)}

    # Plot using Plotly
    for t in types:
        fig.add_trace(
            go.Bar(
                x=bin_centers,
                y=counts[t].values,
                name=t,
                marker=dict(color=type_colors[t]),
            )
        )

    fig.update_layout(
        barmode="stack",
        # title="Point Data Distribution",
        xaxis=dict(
            title="Distance [m]",
            range=[range_el[0], range_el[1]],
            showgrid=True,
        ),
        yaxis=dict(
            title="Count",
            showgrid=True,
        ),
        legend=dict(
            itemclick=False,  # Disable click interactions in the legend
            itemdoubleclick=False,  # Disable double-click interactions in the legend
            title=col[0],
        ),
        template="plotly_white",
        height=fig_height,
        margin=dict(l=0, r=0, t=0, b=0),
    )


def plot_elevation(fig, profile_df):
    """
    Plot elevation profile using Plotly.

    Parameters:s
        profile_df : DataFrame with 'dist_m' (distance) and 'elevation' columns
    """

    # Add elevation line
    fig.add_trace(
        go.Scatter(
            x=profile_df["dist_m"],
            y=profile_df["elevation"],
            mode="lines",
            name="Elevation",
            line=dict(color="black"),
        )
    )

    # Update layout
    fig.update_layout(
        title="Profile d'élévation",
        xaxis=dict(
            title="Distance [m]",
            range=[profile_df["dist_m"].min(), profile_df["dist_m"].max()],
            showgrid=True,
        ),
        yaxis=dict(
            title="Elevation [m]",
            range=[profile_df["elevation"].min(), profile_df["elevation"].max() + 5],
            showgrid=True,
            automargin=True,
        ),
        template="plotly_white",
        height=300,
        showlegend=True,  # <-- Add this line
        legend=dict(
            itemclick=False,  # Disable click interactions in the legend
            itemdoubleclick=False,  # Disable double-click interactions in the legend
            title="Bisse",
        ),
        margin=dict(l=0),
    )

    # Show the plot
    # fig.show()
