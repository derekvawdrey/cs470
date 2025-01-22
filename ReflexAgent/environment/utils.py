import numpy as np

def minimized_angle(theta):
    return (theta + 3*np.pi)%(2*np.pi)-np.pi

def rotation_matrix(angle_radians):
    return np.array([
        [np.cos(angle_radians), -np.sin(angle_radians)],
        [np.sin(angle_radians), np.cos(angle_radians)]
    ])