import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.animation import FuncAnimation
import numpy as np

from worldview import WorldView

mpl.rcParams['toolbar'] = 'None'

view = WorldView()

ani = FuncAnimation(view.fig, view.update, frames=np.arange(0, 2000), interval=10, blit=True)

plt.show()
