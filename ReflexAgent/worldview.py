import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.widgets import Button, CheckButtons, RadioButtons
from matplotlib.backend_bases import MouseButton
from matplotlib.gridspec import GridSpec
import numpy as np
import os

from environment.environment import Environment
from environment.robot import RobotArtist
from environment.obstacle import ObstacleArtist
from environment.goal import GoalArtist
from environment.utils import rotation_matrix

from agents.agentregistry import agent_register

class WorldView:
    def __init__(self,):
        self.env = Environment()
        self.obstacle_artists = {}
        self.robot_artists = {}
        self.goal_artists = {}
        width = 15
        height = 10
        self.fig = plt.figure(figsize=(width, height), dpi=100)
        gs = GridSpec(height, width, figure=self.fig)
        self.world_ax = self.fig.add_subplot(gs[:, :height])
        self.world_ax.axis('off')
        self.field_loaded = False

        self.ax_record_btn = self.fig.add_subplot(gs[1, height:height+2])
        self.record_btn = Button(self.ax_record_btn, "Stop Recording" if self.env.recording else "Start Recording")
        self.record_btn.on_clicked(self.toggle_recording)

        self.ax_save_btn = self.fig.add_subplot(gs[1, height+2:height+5])
        self.save_btn = Button(self.ax_save_btn, "Save Recording")
        self.save_btn.on_clicked(self.save_recording)

        self.ax_clear_record_btn = self.fig.add_subplot(gs[2, height:height+2])
        self.clear_record_btn = Button(self.ax_clear_record_btn, "Clear Recording")
        self.clear_record_btn.on_clicked(self.clear_recording)

        self.ax_record_size = self.fig.add_subplot(gs[2, height+2:height+5], facecolor='m')
        self.ax_record_size.axis('off')
        self.records_text = self.ax_record_size.text(0, 0, f'Records: {self.env.get_record_size()}', size=16, ha='center', va='center')
        self.ax_record_size.set_xlim(-1, 1)
        self.ax_record_size.set_ylim(-1, 1)

        self.ax_reset_btn = self.fig.add_subplot(gs[3, height:height+2])
        self.reset_btn = Button(self.ax_reset_btn, "Reset Steps")
        self.reset_btn.on_clicked(self.reset_steps)

        self.ax_steps = self.fig.add_subplot(gs[3, height+2:height+5], facecolor='m')
        self.ax_steps.axis('off')
        self.steps_text = self.ax_steps.text(0, 0, f'Steps: {self.env.get_step_count()}', size=16, ha='center', va='center')
        self.ax_steps.set_xlim(-1, 1)
        self.ax_steps.set_ylim(-1, 1)

        maps_list = [f.split('.', 1)[0] for f in os.listdir('./maps')]
        self.ax_map_select = self.fig.add_subplot(gs[4:height-3, height:height+2])
        self.map_select_radio = RadioButtons(self.ax_map_select, labels=maps_list, active=0)
        self.map_select_radio.on_clicked(self._load_maze)

        agent_list = [agent_name for agent_name in agent_register.keys()]
        default_agent_name = "Random Agent"
        self.ax_agent_select = self.fig.add_subplot(gs[4:height-3, height+2:height+5])
        self.agent_select_radio = RadioButtons(self.ax_agent_select, labels=agent_list, active=agent_list.index(default_agent_name))
        self.agent_select_radio.on_clicked(self._switch_agent)

        self.fig.canvas.mpl_connect('key_press_event', self.on_key)

        self.fig.canvas.mpl_connect('button_press_event', self.on_click)

        self.options = {
            "Display Obstacles": True,
            "Display Policy": False,
            "Agent Movement": False
        }
        self.ax_options = self.fig.add_subplot(gs[height-2:height-1, height:height+2])
        self.options_checks = CheckButtons(self.ax_options, labels=self.options.keys(), actives=self.options.values())
        self.options_checks.on_clicked(self._on_click_options)

        self.quiver = None
        self.active_agent = agent_register[default_agent_name]["class"]()
        self.agent_override = agent_register[default_agent_name]["metadata"]["override_delay"]
        plt.tight_layout()

        self._load_maze(maps_list[0])

    def toggle_recording(self, event):
        self.env.recording = not self.env.recording
        self.record_btn.label.set_text("Stop Recording" if self.env.recording else "Start Recording")

    def clear_recording(self, event):
        self.env.reset_record()

    def reset_steps(self, event):
        self.env.reset_steps()

    def save_recording(self, event):
        self.save_btn.label.set_text("Saving...")
        plt.draw()
        self.env.save_record()
        self.save_btn.label.set_text("Save Recording")

    def update(self, frame_count):
        if self.options["Agent Movement"] and self.active_agent is not None:
            robot_pos, goal_pos, dist_sensors = self.env.get_robot_data()
            self.env.update({
                "trajectory": self.active_agent.act(robot_pos, goal_pos, dist_sensors),
                "override": self.agent_override,
                "category": "AGENT"
            })
        self.steps_text.set_text(f'Steps: {self.env.get_step_count()}')
        self.records_text.set_text(f'Records: {self.env.get_record_size()}')
        if not self.field_loaded and self.options["Display Policy"]:
            self._draw_field()
        artists = [self.steps_text, self.records_text, self.quiver]
        artists.append(self.goal_artists[self.env.goal.id].update(self.env.goal))
        artists.extend(self.robot_artists[self.env.robot.id].update(self.env.robot, self.env.obstacles))
        for obstacle in self.env.obstacles:
            obs_artist = self.obstacle_artists[obstacle.id].update(obstacle)
            obs_artist.set_visible(self.options["Display Obstacles"])
            artists.append(obs_artist)

        return artists

    def on_key(self, event):
        if event.key == 'up':
            if not self.options["Agent Movement"]:
                self.env.update({
                    "trajectory": self.env.robot.heading,
                    "override": True,
                    "category": "UP"
                })
        elif event.key == 'right':
            if not self.options["Agent Movement"]:
                robot_heading = self.env.robot.heading
                robot_right = rotation_matrix(np.radians(-90)) @ robot_heading
                self.env.update({
                    "trajectory": robot_right,
                    "override": True,
                    "category": "RIGHT"
                })
        elif event.key == 'left':
            if not self.options["Agent Movement"]:
                robot_heading = self.env.robot.heading
                robot_left = rotation_matrix(np.radians(90)) @ robot_heading
                self.env.update({
                    "trajectory": robot_left,
                    "override": True,
                    "category": "LEFT"
                })
        elif event.key == 'down':
            if not self.options["Agent Movement"]:
                self.env.update({
                    "trajectory": np.zeros(2),
                    "override": True,
                    "category": "STOP"
                })
        elif event.key == 'p':
            if self.quiver is not None:
                self.options_checks.set_active(list(self.options.keys()).index("Display Policy"))
        elif event.key == 'a':
            self.options_checks.set_active(list(self.options.keys()).index("Agent Movement"))

    def on_click(self, event):
        if event.button is MouseButton.RIGHT:
            if event.xdata is not None and event.ydata is not None:
                self.env.set_robot_pos(np.array([event.xdata, event.ydata]))

    def _switch_agent(self, agent_name):
        self.active_agent = agent_register[agent_name]["class"]()
        self.agent_override = agent_register[agent_name]["metadata"]["override_delay"]
        self._draw_field()

    def _on_click_options(self, clicked_label):
        self.options[clicked_label] = not self.options[clicked_label]
        if clicked_label == "Display Policy" and self.quiver is not None:
            self.quiver.set_visible(self.options["Display Policy"])

    def _load_maze(self, filename):
        self.env.load_file(f'{filename}.json')

        self.goal_artists = {
            self.env.goal.id: GoalArtist()
        }
        goal_patch = self.goal_artists[self.env.goal.id].setup(self.env.goal)
        self.world_ax.add_patch(goal_patch)

        self.robot_artists = {
            self.env.robot.id: RobotArtist()
        }
        robot_patches = self.robot_artists[self.env.robot.id].setup(self.env.robot, self.env.obstacles)
        for patch in robot_patches:
            self.world_ax.add_patch(patch)

        xmin, xmax = float('inf'), float('-inf')
        ymin, ymax = float('inf'), float('-inf')

        self.obstacle_artists = {}

        self._draw_field()

        for obstacle in self.env.obstacles:
            self.obstacle_artists[obstacle.id] = ObstacleArtist()
            obstacle_patch = self.obstacle_artists[obstacle.id].setup(obstacle)
            self.world_ax.add_patch(obstacle_patch)
            xmin = np.amin([xmin, obstacle.start_pos[0], obstacle.end_pos[0]])
            ymin = np.amin([ymin, obstacle.start_pos[1], obstacle.end_pos[1]])
            xmax = np.amax([xmax, obstacle.start_pos[0], obstacle.end_pos[0]])
            ymax = np.amax([ymax, obstacle.start_pos[1], obstacle.end_pos[1]])

        offset = 2
        self.world_ax.set_xlim(xmin - offset, xmax + offset)
        self.world_ax.set_ylim(ymin - offset, ymax + offset)

    def _draw_field(self):
        if self.active_agent is not None:
            arrow_scale = 3
            X, Y, U, V = self.env.get_action_field(self.active_agent, force_load=self.options["Display Policy"])
            self.field_loaded = self.options["Display Policy"]
            self.quiver = self.world_ax.quiver(X, Y, U, V, angles='xy', scale_units='xy', scale=1/arrow_scale, color=(0.75, 0.0, 0.0))
            self.quiver.set_visible(self.options["Display Policy"])
