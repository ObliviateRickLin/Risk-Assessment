
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401 unused import

from collision_octagon import CollisionOctagon

# Modify the visualization function to close the polygons for ego_car and other_car
def visualize_collision_octagon(ax, collision_octagon_obj, title=""):
    """
    Visualize the collision octagon and the two cars involved.
    
    Parameters:
    - ax: Matplotlib axis object where the plot will be drawn.
    - collision_octagon_obj: An instance of the CollisionOctagon class.
    - title: Title of the subplot.
    """
    # Retrieve attributes from the CollisionOctagon object
    collision_octagon = collision_octagon_obj.collision_octagon
    ego_car = collision_octagon_obj.ego_car
    other_car_rotated = collision_octagon_obj.other_car

    # Plot the ego car (blue) and close the polygon
    ax.plot(*zip(*ego_car, ego_car[0]), 'b-', label="Ego Car")
    
    # Plot the other car (red) and close the polygon
    ax.plot(*zip(*other_car_rotated, other_car_rotated[0]), 'r-', label="Other Car")
    
    # Plot the collision octagon (green) and close the polygon
    ax.plot(*zip(*collision_octagon, collision_octagon[0]), 'g-', label="Collision Octagon")
    
    # Additional plot settings
    ax.set_xlabel('x')
    ax.set_ylabel('y')
    ax.set_title(title)
    ax.legend()
    ax.grid(True)
    ax.set_aspect('equal', adjustable='box')

def plot_gaussian_and_integration_region(collision_octagon_obj, ax, mu_x=0, mu_y=0, sigma_x=1.0, sigma_y=1.0):
    # Create a grid of x and y values, ranging from -10 to 10
    x = np.linspace(-10, 10, 100)
    y = np.linspace(-10, 10, 100)
    x, y = np.meshgrid(x, y)

    # Compute the values of the Gaussian distribution on the grid
    z = (1 / (2 * np.pi * sigma_x * sigma_y)) * np.exp(-0.5 * (((x-mu_x)/sigma_x)**2 + ((y-mu_y)/sigma_y)**2))
    
    # Get collision_octagon vertices
    collision_octagon = collision_octagon_obj.collision_octagon
    
    # Create a path for the collision octagon
    from matplotlib.path import Path
    path = Path(collision_octagon)

    # Create a grid of points
    points = np.column_stack((x.ravel(), y.ravel()))

    # Check which points are inside the collision octagon
    mask = path.contains_points(points).reshape(100, 100)

    # Create a color array based on the mask
    colors = np.zeros((100, 100, 4))
    colors[mask] = [1, 0, 0, 0.3]  # RGBA color for the integration region

    # Plot the Gaussian distribution on the given subplot
    ax.plot_surface(x, y, z, facecolors=colors, rstride=1, cstride=1, alpha=0.5)

    # Plot the projection of the integration region on the x-y plane
    ax.plot_surface(x, y, z * 0, facecolors=colors, rstride=1, cstride=1, alpha=0.3, zorder=0.1)

    # Set the labels and title
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Probability Density')


if __name__ == "__main__":
    # Base car definitions
    ego_car = np.array([[-1, -0.5], [1, -0.5], [1, 0.5], [-1, 0.5]])
    other_car = np.array([[2, 0.5], [3, 1.5], [2, 2.5], [1, 1.5]])

    test_cases = [
        (ego_car, other_car, "Two cars parallel in different lanes"),
        (ego_car, np.array([[2, -1.5], [3, -0.5], [2, 0.5], [1, -0.5]]), "Two cars heading towards each other"),
        (ego_car, np.array([[2, 1], [3, 2], [2, 3], [1, 2]]), "Other car in front of ego car"),
        (ego_car, np.array([[-3, -0.5], [-2, 0.5], [-3, 1.5], [-4, 0.5]]), "Other car to the left of ego car")
    ]

    # First 2x2 plot for visualize_collision_octagon
    fig1, axes1 = plt.subplots(2, 2, figsize=(10, 10))
    for i, (ego, other, title) in enumerate(test_cases):
        ax1 = axes1[i//2, i%2]
        collision_octagon_obj = CollisionOctagon(ego, other)
        visualize_collision_octagon(ax1, collision_octagon_obj, title)
    plt.show()

    # Second 2x2 plot for plot_gaussian_and_integration_region_subplot
    fig2 = plt.figure(figsize=(10, 10))
    for i, (ego, other, title) in enumerate(test_cases):
        ax2 = fig2.add_subplot(2, 2, i + 1, projection='3d')
        ax2.set_title(title)
        collision_octagon_obj = CollisionOctagon(ego, other)
        plot_gaussian_and_integration_region(collision_octagon_obj, ax2, mu_x=0, mu_y=0, sigma_x=2.0, sigma_y=1.0)
    plt.show()

