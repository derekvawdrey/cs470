import numpy as np
import matplotlib.pyplot as plt

from .basicgeometry import BasicCircle

class GoalArtist:
    def __init__(self):
        self.artist = None

    def setup(self, goal):
        self.artist = plt.Circle(
            goal.position, 
            goal.radius,
            facecolor='green',
            alpha=0.5,
            fill=True
        )
        return self.artist

    def update(self, goal):
        self.artist.center = goal.position
        return self.artist

class Goal(BasicCircle):
    def __init__(self, id, position, radius):
        super().__init__(position, radius)
        self.id = id

    def get_json(self):
        return {
            "id": self.id,
            "position": tuple(self.position),
            "radius": self.radius
        }    