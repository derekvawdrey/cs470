import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import ConnectionPatch

from .basicgeometry import LineSegment

class ObstacleArtist:
    def __init__(self):
        self.artist = None

    def setup(self, obstacle):
        self.artist = ConnectionPatch(
            obstacle.start_pos, 
            obstacle.end_pos, 
            'data', 
            'data', 
            color=obstacle.rgb, 
            alpha=1.0,
            linewidth=2
        )
        return self.artist
    
    def update(self, obstacle):
        self.artist.xy1 = obstacle.start_pos
        self.artist.xy2 = obstacle.end_pos
        return self.artist


class Obstacle(LineSegment):
    def __init__(self, id, start_pos, end_pos, rgb):
        super().__init__(start_pos, end_pos)
        self.rgb = rgb
        self.id = id

    def get_json(self):
        return {
            "id": self.id,
            "color": self.rgb,
            "start_pos": tuple(self.start_pos),
            "end_pos": tuple(self.end_pos)
        }    