# Overview
For this project we'll be creating two reflex agents that will guide a simple robot to a goal position while avoiding walls. The methods we will explore are potential fields and supervised machine learning. \\
The project consists of a UI that displays the robot and world along with controls for recording data, moving the robot, and displaying an approximation of the robot's movement policy. \\
Beyond the buttons on the UI the following controls are avaliable: \\
a: toggles automatic agent movement based on the agent selected in the UI. Human input will be disabled when the robot is moving under agent direction. \\
p: toggles the display of the agent policy based on the agent selecting in the UI \\
Arrow keys: \\
* up: move the robot forward \\
* left: rotate counter clockwise \\
* right: rotate clockwise \\
* back: enters a trajectory of (0, 0) used for instructing the machine learning agent to stop in the goal region \\

right mouse click: in the world region will move the robot to that position as long as it would not result in the robot colliding with any walls in the environment. \\
The UI is build with python3 on matplotlib 3.8.0 so it may be a tad slow at times. Beyond that the only packages needed are numpy, pickle, pandas and scikit-learn. \\
Usage is as follows: \\
```
python main.py
```

# The Robot
The robot for this project is a simples circle robot that exists in a 2d world. It's actions are limited rotation and moving forward. It detects the world using a series of 16 distance sensors arranged in a circle around the robot at even intervals starting from the robot's right side. The objective is to manuever the robot to the goal position indicated by the green circle.\\
Agents for the robot are contained under the agents directory and registered with the UI by agentregistry.py you shouldn't need to change anything in the file unless you want to add new agents or multiple different machine learning agents. \\
## User Actions
For gathering data and exploring how the robot moves the robot will. We'll use the arrow keys to direct the robot around the world while we record each step. Steps occur when a key is pressed incrementing the records count. By default when the data records are saved they will be placed in the data folder named according to the time that the record was made. Saving a dataset does not clear the current data recording from the UI. \\

## Trajectory Following
In general the robot follows a trajectory as a command. It will rotate until is is facing the direction indicated by the trajectory then take a step forward, this may take multiple steps as indicated by the step count. This can be overriden by changing the *override_delay* parameter in agentregistry.py for the corresponding agent. It is not recommended to change these settings. In general if an agent is acting in line with human commands then *override_delay* is recommended. In the case of potential fields *override_delay* is disabled. It may also be advised to set *override_delay* if a machine learning agent is predicting trajectories instead of user commands. \\

# Agent Types
Each agent we create will need to decide what to do based on the following information. \\
**ccw: counter clock wise \\
 \\
robot_pos: the robots pose defined as \\
```
robot_pos = [robot position x, robot position y, robot rotation in degrees ccw]
```
goal_pos: the goal pose defined as \\
```
goal_pos = [goal position x, goal position y]
```
dist_sensors: an array of the current state of our distance sensors where each entry corresponds to the distance reading of a sensor placed in a ring around our robot in ccw fashion starting from the robot's right side. \\
For example:  \\
dist_sensors[0] gives the distance reading directly to the robot's right \\
dist_sensors[4] gives the distance reading direclty in front of the robot \\
dist_sensors[8] gives the distance reading direclty to the robot's left \\
dist_sensors[12] gives the distance reading direclty behind the robot \\

## Potential Fields
We'll be implementing the potential fields method to guide our robot to the goal. Further infromation on this can be found in the reading on learningsuite.

## Machine Learning
For the machine learing agent we'll load the data use Pandas and train models from scikit-learn. The following link has a list of the models included in scikit-learn https://scikit-learn.org/stable/supervised_learning.html if you are unfamiliar with machine learning, don't worry you'll just be using the Classifier models (indicated by the class name) then fit the data using that model, the basics of which have been provided. \\
What we'll do is explore the impact of the data, different features, and different models on the performance of our agent. \\
Feature engineering will be done using Pandas. Pandas is a library for loading and working with data from csv files. The prinicple object in pandas is a dataframe. For feature engineering you'll create new colums in the dataframe. And example is provided below where we take all the values for *x* and *y* in our dataframe and create a new column *z* that is a function of *x* and *y*. We'll want to think about how different represenations and features of data may be beneficial to our model and make learning how to guide the robot to the goal easier. \\
```
df["z"] = np.sqrt(np.sin(df["x"]) + np.cos(df["y"]))
```

Further information about Pandas can be found here: https://pandas.pydata.org/pandas-docs/stable/user_guide/10min.html \\

We do include functions to save and load ml models using pickle. By default the models are save under the models directory. \\

### Data Recording

Within the UI we will use the `Start Recording` button to beging recording each step taken by you robot. The recording will include the data that the agent would receive and use to make its decision i.e. the robot's pose, the goal pose, the distance sensor data, the step number, the command type, the resulting tajectory. The records count should increment if the recording is running. \\
Importantly the command type is what we will try to learn, this will consist of "UP", "LEFT", "RIGHT", and "STOP". This is assuming that a human was controling the robot for the duration of the recording, if you record while an agent is in control of the robot then the command type will be "AGENT". \\


# TODO:
[ ] implement the potential fields agent `\agents\pfagent.py` \\
[ ] gather data using the UI \\
[ ] train the machine learning agent `\agents\mlagent.py` \\
