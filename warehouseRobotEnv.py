'''
Custom Gym environment
https://gymnasium.farama.org/tutorials/gymnasium_basics/environment_creation/
'''

'''
The gymnasium library, imported as 'gym', is a popular open-source library for developing and comparing reinforcement learning algorithms. 
It provides a wide range of environments for testing and benchmarking RL algorithms. 
The library is designed to facilitate research in RL by providing a standardized interface for environments and algorithms.
'''
# Import the gymnasium library as 'gym'
import gymnasium as gym

'''
The spaces module in gymnasium defines the types of spaces that can be used in environments. 
Spaces are used to describe the observation and action spaces of an environment. 
They are crucial for defining the structure of the environment and the types of inputs and outputs it can handle.
'''
# Import the spaces module from gymnasium
from gymnasium import spaces

'''
The register function is used to register new environments with gym. 
This allows custom environments to be added to the gym library, making them available for use with gym's algorithms and tools. 
Registering an environment involves providing metadata about the environment, such as its name, the number of states and actions, and any additional parameters.
'''
# Import the register function from gymnasium.envs.registration
from gymnasium.envs.registration import register

'''
The check_env function is a utility function provided by gymnasium for validating the structure of custom environments. 
It checks if an environment conforms to the gym standard, ensuring that it has the correct types of spaces and methods. 
This is useful for debugging and ensuring compatibility with gym's algorithms and tools.
'''
# Import the check_env function from gymnasium.utils.env_checker
from gymnasium.utils.env_checker import check_env

'''
The warehouseRobot module is presumably a custom module developed for a specific application, related to controlling or simulating a warehouse robot. 
'''
# Import the warehouseRobot module as 'wr'
import warehouseRobot as wr

'''
The numpy library, imported as 'np', is a fundamental package for scientific computing in Python. 
It provides support for arrays, matrices, and many mathematical functions to operate on these data structures efficiently. 
Numpy is widely used in data analysis, machine learning, and numerical simulations, among other fields.
'''
# Import the numpy library as 'np'
import numpy as np

# Register this module as a gym environment. Once registered, the id is usable in gym.make().
register(
    id='warehouse-robot-v0',                                # call it whatever you want
    entry_point='warehouseRobotEnv:WarehouseRobotEnv', # module_name:class_name
)

# Implement our own gym env, must inherit from gym.Env
# https://gymnasium.farama.org/api/env/
class WarehouseRobotEnv(gym.Env):
    # metadata is a required attribute
    # render_modes in our environment is either None or 'human'.
    # render_fps is not used in our env, but we are require to declare a non-zero value.
    metadata = {"render_modes": ["human"], 'render_fps': 4}

    def __init__(self, grid_rows=4, grid_cols=5, render_mode=None):

        self.grid_rows=grid_rows
        self.grid_cols=grid_cols
        self.render_mode = render_mode

        # Initialize the WarehouseRobot problem
        self.warehouse_robot = wr.WarehouseRobot(grid_rows=grid_rows, grid_cols=grid_cols, fps=self.metadata['render_fps'])

        # Gym requires defining the action space. The action space is robot's set of possible actions.
        # Training code can call action_space.sample() to randomly select an action. 
        self.action_space = spaces.Discrete(len(wr.RobotAction))

        # Gym requires defining the observation space. The observation space consists of the robot's and target's set of possible positions.
        # The observation space is used to validate the observation returned by reset() and step().
        # Use a 1D vector: [robot_row_pos, robot_col_pos, target_row_pos, target_col_pos]
        self.observation_space = spaces.Box(
            low=0,
            high=np.array([self.grid_rows-1, self.grid_cols-1, self.grid_rows-1, self.grid_cols-1]),
            shape=(4,),
            dtype=np.int32
        )

    # Gym required function (and parameters) to reset the environment
    def reset(self, seed=None, options=None):
        super().reset(seed=seed) # gym requires this call to control randomness and reproduce scenarios.

        # Reset the WarehouseRobot. Optionally, pass in seed control randomness and reproduce scenarios.
        self.warehouse_robot.reset(seed=seed)

        # Construct the observation state:
        # [robot_row_pos, robot_col_pos, target_row_pos, target_col_pos]
        obs = np.concatenate((self.warehouse_robot.robot_pos, self.warehouse_robot.target_pos))
        
        # Additional info to return. For debugging or whatever.
        info = {}

        # Render environment
        if(self.render_mode=='human'):
            self.render()

        # Return observation and info
        return obs, info

    # Gym required function (and parameters) to perform an action
    def step(self, action):
        # Perform action
        target_reached = self.warehouse_robot.perform_action(wr.RobotAction(action))

        # Determine reward and termination
        reward=0
        terminated=False
        if target_reached:
            reward=1
            terminated=True

        # Construct the observation state: 
        # [robot_row_pos, robot_col_pos, target_row_pos, target_col_pos]
        obs = np.concatenate((self.warehouse_robot.robot_pos, self.warehouse_robot.target_pos))

        # Additional info to return. For debugging or whatever.
        info = {}

        # Render environment
        if(self.render_mode=='human'):
            print(wr.RobotAction(action))
            self.render()

        # Return observation, reward, terminated, truncated (not used), info
        return obs, reward, terminated, False, info

    # Gym required function to render environment
    def render(self):
        self.warehouse_robot.render()

# For unit testing
if __name__=="__main__":
    env = gym.make('warehouse-robot-v0', render_mode='human')

    # Use this to check our custom environment
    # print("Check environment begin")
    # check_env(env.unwrapped)
    # print("Check environment end")

    # Reset environment
    obs = env.reset()[0]

    # Take some random actions
    while(True):
        rand_action = env.action_space.sample()
        obs, reward, terminated, _, _ = env.step(rand_action)

        if(terminated):
            obs = env.reset()[0]