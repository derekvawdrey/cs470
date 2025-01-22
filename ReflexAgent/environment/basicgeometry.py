
import numpy as np
import warnings

from .utils import minimized_angle, rotation_matrix

def ccw(a, b, c):
    return (c[1] - a[1]) * (b[0] - a[0]) > (b[1] - a[1]) * (c[0] - a[0])

def on_segment(p, q, r):
    return (min(p[0], r[0]) <= q[0] <= max(p[0], r[0]) and
            min(p[1], r[1]) <= q[1] <= max(p[1], r[1]))

def intersection_point(p1, p2, q1, q2):
    A1 = p2[1] - p1[1]
    B1 = p1[0] - p2[0]
    C1 = A1 * p1[0] + B1 * p1[1]
    
    A2 = q2[1] - q1[1]
    B2 = q1[0] - q2[0]
    C2 = A2 * q1[0] + B2 * q1[1]
    
    determinant = A1 * B2 - A2 * B1
    if determinant == 0:
        return None
    
    x = (B2 * C1 - B1 * C2) / determinant
    y = (A1 * C2 - A2 * C1) / determinant
    return (x, y)

def _line_segments_intersect(p1, p2, q1, q2):
    intersect = (ccw(p1, q1, q2) != ccw(p2, q1, q2)) and (ccw(p1, p2, q1) != ccw(p1, p2, q2))
    
    if not intersect:
        return False, None
    
    point = intersection_point(p1, p2, q1, q2)
    if point is not None:
        return True, point
    
    return False, None

def _line_circle_intersect(x1, y1, x2, y2, cx, cy, r):
    x1 -= cx
    y1 -= cy
    x2 -= cx
    y2 -= cy
    
    dx = x2 - x1
    dy = y2 - y1
    a = dx**2 + dy**2
    b = 2 * (x1 * dx + y1 * dy)
    c = x1**2 + y1**2 - r**2
    
    discriminant = b**2 - 4 * a * c
    if discriminant < 0:
        return False
    
    t1 = (-b - np.sqrt(discriminant)) / (2 * a)
    t2 = (-b + np.sqrt(discriminant)) / (2 * a)
    
    return 0 <= t1 <= 1 or 0 <= t2 <= 1

class LineSegment:
    def __init__(self, start_pos, end_pos):
        self.start_pos = np.asarray(start_pos)
        self.end_pos = np.asarray(end_pos)

    def check_intersection(self, other):
        if issubclass(other.__class__, LineSegment):
            return _line_segments_intersect(self.start_pos, self.end_pos, other.start_pos, other.end_pos)
        elif issubclass(other.__class__, BasicCircle):
            return _line_circle_intersect(*self.start_pos, *self.end_pos, *other.position, other.radius), None
        else:
            warnings.warn(f"Unkown geometry object `{other.__class__}` in check_intersection ")
            return False, None

    def get_length(self):
        return np.linalg.norm(self.end_pos - self.start_pos, ord=2)

class BasicCircle:
    def __init__(self, position, radius):
        self.position = np.array(position, dtype=float)
        self.radius = radius

    def randomize_position(self, x_bounds, y_bounds):
        self.position = np.array([
            np.random.uniform(x_bounds[0], x_bounds[1]),
            np.random.uniform(y_bounds[0], y_bounds[1])
        ])

    def overlaps_with(self, other_circle):
        distance = np.linalg.norm(self.position - other_circle.position)
        return distance < (self.radius + other_circle.radius)
    
    def check_intersection(self, other):
        if issubclass(other.__class__, BasicCircle):
            return self.overlaps_with(other), None
        elif issubclass(other.__class__, LineSegment):
            return _line_circle_intersect(*other.start_pos, *other.end_pos, *self.position, self.radius), None
        else:
            warnings.warn(f"Unkown geometry object `{other.__class__}` in check_intersection ")
            return False, None

    def distance_to(self, other_circle):
        return np.linalg.norm(self.position - other_circle.position)

class OrientedCircle(BasicCircle):
    def __init__(self, position, radius, heading):
        super().__init__(position, radius)
        self.heading = np.array(heading, dtype=float) / np.linalg.norm(heading)
        self.rotation_matrix = rotation_matrix(np.arctan2(self.heading[1], self.heading[0]))

    def rotate_heading(self, angle_radians):
        self.rotation_matrix = rotation_matrix(angle_radians)
        self.heading = self.rotation_matrix @ self.heading

    def angle_to(self, other_circle):
        vector_to_other = other_circle.position - self.position
        vector_to_other /= np.linalg.norm(vector_to_other)
        dot_product = np.dot(self.heading, vector_to_other)
        angle_radians = np.arccos(np.clip(dot_product, -1.0, 1.0))
        cross_product = self.heading[0] * vector_to_other[1] - self.heading[1] * vector_to_other[0]
        return np.sign(cross_product) * minimized_angle(angle_radians)
