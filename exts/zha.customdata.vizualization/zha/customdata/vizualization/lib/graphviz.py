import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
from matplotlib.cm import ScalarMappable
from matplotlib.colors import Normalize
from matplotlib.patches import Wedge
from PIL import Image



def plot_value_distribution_transparent(data: np.array, 
                            cmap='viridis', 
                            bins: int = 20, 
                            xlabel: str = 'Values', 
                            ylabel: str = 'Frequency', 
                            title: str = 'Distribution of Values',
                            vertical_lines: bool = False):
    """
    Plot the distribution of values with red vertical lines at each fifth.

    Parameters:
    data: np.array of shape (N,)
    cmap: str, colormap name (default: 'viridis')
    bins: int, number of bins for histogram (default: 20)
    xlabel: str, label for x-axis (default: 'Values')
    ylabel: str, label for y-axis (default: 'Frequency')
    title: str, title of the plot (default: 'Distribution of Values')
    vertical_lines: bool, whether to add red vertical lines at each fifth of the graph (default: False)
    """
    
    # Create a figure with a transparent background
    fig, ax = plt.subplots(figsize=(10, 6))
    fig.patch.set_alpha(0)
    ax.patch.set_alpha(0)

    n, bins, patches = ax.hist(data, bins)
    bin_centers = 0.5 * (bins[:-1] + bins[1:])
    
    # Create a normalized colormap
    norm = Normalize(vmin=min(bin_centers), vmax=max(bin_centers))
    sm = ScalarMappable(norm=norm, cmap=cmap)
    sm.set_array([])

    # Apply colors to patches
    for bin_center, patch in zip(bin_centers, patches):
        color = sm.to_rgba(bin_center)
        patch.set_facecolor(color)
    
    # Add red vertical lines at each fifth of the graph
    if vertical_lines:
        x_min, x_max = ax.get_xlim()
        for i in range(1, 5):
            x = x_min + i * (x_max - x_min) / 5
            ax.axvline(x=x, color='red', linestyle='--', linewidth=1)
    
    # Add colorbar with white text and ticks
    cbar = plt.colorbar(sm)
    cbar.ax.yaxis.set_tick_params(color='white')
    plt.setp(plt.getp(cbar.ax.axes, 'yticklabels'), color='white')
    
    # Set labels and title color to white
    ax.set_xlabel(xlabel, color='white')
    ax.set_ylabel(ylabel, color='white')
    ax.set_title(title, color='white')
    
    # Set tick colors to white
    ax.tick_params(axis='x', colors='white')
    ax.tick_params(axis='y', colors='white')
    
    # Make the box around the plot white
    for spine in ax.spines.values():
        spine.set_edgecolor('white')
    
    # Use tight layout
    plt.tight_layout()
    
    # Convert the plt to a PIL image with transparency
    fig.canvas.draw()
    width, height = fig.canvas.get_width_height()
    buffer = fig.canvas.buffer_rgba()
    img = Image.frombuffer('RGBA', (width, height), buffer)
    
    plt.close(fig)  # Close the figure to free up memory
    return img

# needs to be tested
def plot_donut_chart_transparent(data, num_bins=5, 
                                num_sub_wedges=200, 
                                gap_size=0.01, 
                                cmap='viridis', 
                                custom_labels=None,
                                title=None):
    # Ensure data is a numpy array
    data = np.array(data)


    if num_bins > 7:
        raise ValueError("The number of bins cannot be more than 7.")
    if num_bins < 2:
        raise ValueError("The number of bins cannot be less than 2.")
    
    if custom_labels is None:
        if num_bins == 2:
            custom_labels = ["Low", "High"]
        elif num_bins == 3:
            custom_labels = ["Low", "Medium", "High"]
        elif num_bins == 4:
            custom_labels = ["Very low", "Low", "High", "Very high"]
        elif num_bins == 5:
            custom_labels = ["Very low", "Low", "Medium", "High", "Very high"]
        elif num_bins == 6:
            custom_labels = ["Very low", "Low", "Medium low", "Medium high", "High", "Very high"]
        elif num_bins == 7:
            custom_labels = ["Very low", "Low", "Medium low", "Medium", "Medium high", "High", "Very high"]
    
    if num_bins != len(custom_labels):
        raise ValueError("The number of bins must match the number of custom labels.")
    
    
    # Create bins and count data points in each bin
    counts, bin_edges = np.histogram(data, bins=num_bins)
    bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2

    # Remove empty bins
    non_empty_indices = counts > 0
    counts = counts[non_empty_indices]
    bin_centers = bin_centers[non_empty_indices]
    bin_edges = np.concatenate(([bin_edges[0]], bin_edges[1:][non_empty_indices]))

    # Create color map
    cmap = plt.get_cmap(cmap)
    norm = Normalize(vmin=bin_edges[0], vmax=bin_edges[-1])

    # Create the figure and axis
    fig, ax = plt.subplots(figsize=(6, 6))
    # Make the figure and axis background transparent
    fig.patch.set_alpha(0)
    ax.patch.set_alpha(0)

    # Calculate total angle for the chart (in degrees)
    total_angle = 360 - (len(counts) * gap_size * 360)  # Subtract total gap size

    # Calculate the starting angle and angle sizes for each main wedge
    start_angle = 90  # Start from the top
    angles = counts / counts.sum() * total_angle

    # Calculate the number of sub-wedges for each main wedge
    sub_wedge_counts = np.round(angles / total_angle * num_sub_wedges).astype(int)

    # Add main wedges and sub-wedges
    for i, (count, angle, num_subs) in enumerate(zip(counts, angles, sub_wedge_counts)):
        # Calculate angles for sub-wedges
        sub_angles = np.linspace(start_angle, start_angle + angle, num_subs + 1)

        # Calculate colors for sub-wedges
        sub_colors = cmap(np.linspace(norm(bin_edges[i]), norm(bin_edges[i+1]), num_subs))

        # Add sub-wedges
        for j in range(num_subs):
            sub_wedge = Wedge((0, 0), 1.0, sub_angles[j], sub_angles[j+1],
                            width=0.5, facecolor=sub_colors[j], edgecolor=sub_colors[j])
            ax.add_artist(sub_wedge)

        # Add percentage label
        midangle = np.deg2rad(start_angle + angle / 2)
        x = 0.75 * np.cos(midangle)
        y = 0.75 * np.sin(midangle)
        percentage = count / counts.sum() * 100
        ax.text(x, y, f"{percentage:.1f}%", ha='center', va='center', fontweight='bold', color='white')

        # Add rotated custom label at the outer edge
        if custom_labels is not None:
            outer_x = 1.3 * np.cos(midangle)
            outer_y = 1.3 * np.sin(midangle)
            label = custom_labels[i] if i < len(custom_labels) else f"Label {i+1}"
            rotation = (start_angle + angle / 2) % 360
            if 90 < rotation < 270:
                rotation = rotation - 180
            ax.text(outer_x, outer_y, label, ha='center', va='center', rotation=rotation,
                    rotation_mode='anchor', color='white')
            
        start_angle += angle + (gap_size * 360)  # Add gap after each main wedge

    # Add title and adjust layout
    if title is not None:
        ax.set_title(title)
    ax.set_xlim(-1.4, 1.4)
    ax.set_ylim(-1.4, 1.4)
    ax.set_aspect('equal')
    ax.axis('off')
    # Use tight layout
    plt.tight_layout()
    
    # Convert the plt to a PIL image with transparency
    fig.canvas.draw()
    width, height = fig.canvas.get_width_height()
    buffer = fig.canvas.buffer_rgba()
    img = Image.frombuffer('RGBA', (width, height), buffer)
    
    plt.close(fig)  # Close the figure to free up memory
    return img



def plot_gradient_sample(cmap_name, width=1024, height=128):
    cmap = plt.get_cmap(cmap_name)
    gradient = np.linspace(0, 1, width)
    gradient = np.vstack([gradient] * height)
    
    # Convert the gradient to RGBA values
    rgba_gradient = cmap(gradient)
    
    # Convert from 0-1 float values to 0-255 uint8
    rgba_gradient = (rgba_gradient * 255).astype(np.uint8)
    
    # Create an image directly from the RGBA array
    img = Image.fromarray(rgba_gradient)
    
    return img