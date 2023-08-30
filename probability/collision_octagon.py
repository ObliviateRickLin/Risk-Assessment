import numpy as np
import matplotlib.pyplot as plt
from scipy import integrate
from scipy.stats import multivariate_normal

class CollisionOctagon:
    
    def __init__(self, ego_car, other_car):
        self.ego_car = ego_car
        self.other_car = other_car
        self.ego_centroid = np.mean(ego_car, axis=0)
        self.other_centroid = np.mean(other_car, axis=0)
        self.collision_octagon = self.init_collision_octagon(ego_car, other_car)
        self.octagon_centroid = np.mean(self.collision_octagon, axis=0)
    
    def __rotate_point(self, point, angle, center_point=(0, 0)):
        angle_rad = np.radians(angle)
        new_point = point - center_point
        new_point = np.array([new_point[0]*np.cos(angle_rad) - new_point[1]*np.sin(angle_rad),
                              new_point[0]*np.sin(angle_rad) + new_point[1]*np.cos(angle_rad)])
        new_point += center_point
        return new_point

    def __intersection_area(self, ego_rect, other_rect):
        xmin = max(ego_rect[:, 0].min(), other_rect[:, 0].min())
        ymin = max(ego_rect[:, 1].min(), other_rect[:, 1].min())
        xmax = min(ego_rect[:, 0].max(), other_rect[:, 0].max())
        ymax = min(ego_rect[:, 1].max(), other_rect[:, 1].max())

        if xmax < xmin or ymax < ymin:
            return 0.0

        return (xmax - xmin) * (ymax - ymin)

    def init_collision_octagon(self, ego_car, other_car):
        collision_octagon = []

        for vertex in other_car:
            for ego_vertex in ego_car:
                translation = vertex - ego_vertex
                translated_ego_car = ego_car + translation

                ego_bbox = [translated_ego_car[:, 0].min(), translated_ego_car[:, 1].min(), translated_ego_car[:, 0].max(), translated_ego_car[:, 1].max()]
                other_bbox = [other_car[:, 0].min(), other_car[:, 1].min(), other_car[:, 0].max(), other_car[:, 1].max()]

                if self.__intersection_area(translated_ego_car, other_car) == 0:
                    collision_octagon.append(translated_ego_car.mean(axis=0))

        collision_octagon = np.array(collision_octagon)
        return self.__sort_octagon_points(collision_octagon)
    
    def __sort_octagon_points(self, collision_octagon):
        centroid = np.mean(collision_octagon, axis=0)
        angles = np.arctan2(collision_octagon[:, 1] - centroid[1], collision_octagon[:, 0] - centroid[0])
        sorted_indices = np.argsort(angles)
        return collision_octagon[sorted_indices]
    
    def __compute_edge_groups(self):
        """
        Private method to compute the edge groups for collision polygon.

        Returns:
        Two lists of edges, each list represents a group.
        """
        collision_octagon = self.collision_octagon

        # Define a function to compute the midpoint of an edge
        def midpoint(edge):
            return [(edge[0][0] + edge[1][0]) / 2, (edge[0][1] + edge[1][1]) / 2]

        # Step 1: Compute all edges
        edges = [(collision_octagon[i % len(collision_octagon)], collision_octagon[(i + 1) % len(collision_octagon)]) for i in range(len(collision_octagon))]

        # Step 2: Remove vertical edges
        edges = [edge for edge in edges if edge[0][0] != edge[1][0]]

        # Step 3: Sort edges based on y-coordinate of midpoint
        edges.sort(key=midpoint)

        # Step 4: Split the edges into two groups
        group1 = [edges[i] for i in range(len(edges)) if i % 2 == 0]
        group2 = [edges[i] for i in range(len(edges)) if i % 2 != 0]

        return group1, group2
    
    def __compute_edge_probability(self, point1, point2, sigma_x, sigma_y):
        m_i = (point2[1] - point1[1]) / (point2[0] - point1[0])
        b_i = point1[1] - m_i * point1[0]
        x_l_i = min(point1[0], point2[0])
        x_u_i = max(point1[0], point2[0])
        
        def y_lower(x):
            return 0

        def y_upper(x):
            return m_i * x + b_i

        def f(x, y):
            return (1 / (2 * np.pi * sigma_x * sigma_y)) * np.exp(-0.5 * ((x/sigma_x)**2 + (y/sigma_y)**2))

        result, _ = integrate.dblquad(f, x_l_i, x_u_i, y_lower, y_upper)
        return result
    
    def compute_CSP(self, sigma_x, sigma_y):
        group1, group2 = self.__compute_edge_groups()
        prob_group1 = sum([self.__compute_edge_probability(edge[0], edge[1], sigma_x, sigma_y) for edge in group1])
        prob_group2 = sum([self.__compute_edge_probability(edge[0], edge[1], sigma_x, sigma_y) for edge in group2])
        CSP = abs(prob_group1 - prob_group2)  # Use the absolute value
        return CSP




