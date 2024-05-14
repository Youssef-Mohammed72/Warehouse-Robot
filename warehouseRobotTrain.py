'''
Example of using Q-Learning or StableBaseline3 to train our custom environment.
'''
# Imports the gym library, which is used to create and manage the custom environment warehouse-robot-v0
import gymnasium as gym

#  Imports the numpy library for numerical operations, including the creation of the Q-table and calculations.
import numpy as np

# Imports matplotlib for plotting the average steps per episode over time, providing a visual representation of the agent's performance.
import matplotlib.pyplot as plt

# Imports the random module for generating random actions during training, specifically when using the epsilon-greedy strategy.
import random

# Imports the pickle module for saving and loading the Q-table to and from disk, allowing for persistence of the trained model.
import pickle

# Imports the custom environment class, even though it's not directly used in the script, to ensure the environment is registered.
import warehouseRobotEnv 

'''
    Function Definition: Defines the run_q function with three parameters: episodes (number of episodes to run),
    is_training (a boolean indicating whether to train or test the agent), 
    and render (a boolean to control rendering of the environment).
'''
def run_q(episodes, is_training=True, render=False):

    '''
        Environment Creation: Creates an instance of the warehouse-robot-v0 environment using gym.make. 
        The render_mode is set to 'human' if render is True, otherwise it's None.
    '''
    env = gym.make('warehouse-robot-v0', render_mode='human' if render else None)

    '''
        Q-Table Initialization: If is_training is True, initializes the Q-table as a 5D array with zeros. 
        If is_training is False, loads the Q-table from a file named 'v0_warehouse_solution.pkl'.
    '''
    if(is_training):
        q = np.zeros((env.unwrapped.grid_rows, env.unwrapped.grid_cols, env.unwrapped.grid_rows, env.unwrapped.grid_cols, env.action_space.n))
    else:
        f = open('v0_warehouse_solution.pkl', 'rb')
        q = pickle.load(f)
        f.close()

    '''
        Hyperparameters: Sets the learning rate (learning_rate_a), discount factor (discount_factor_g), 
        and epsilon for the epsilon-greedy strategy.
    '''
    learning_rate_a = 0.9   # alpha or learning rate
    discount_factor_g = 0.9 # gamma or discount rate. Near 0: more weight/reward placed on immediate state. Near 1: more on future state.
    epsilon = 1             # 1 = 100% random actions

    # Steps Tracker: Initializes an array to track the number of steps taken per episode.
    steps_per_episode = np.zeros(episodes)

    # Episode Loop: Begins a loop to run each episode.
    step_count=0
    for i in range(episodes):
        # Rendering: Prints the current episode number if render is True.
        if(render):
            print(f'Episode {i}')

        # State Reset: Resets the environment to get the initial state and sets a flag terminated to False.
        state = env.reset()[0]
        terminated = False

        # Action Selection Loop: Enters a loop where actions are selected and performed until the episode ends.
        while(not terminated):

            '''
                Action Selection: Uses the epsilon-greedy strategy to select an action. 
                If in training mode and a random number is less than epsilon, a random action is chosen. 
                Otherwise, the action with the highest Q-value for the current state is selected.
            '''
            if is_training and random.random() < epsilon:
                action = env.action_space.sample()
            else:                
                # Convert state of [1,2,3,4] to (1,2,3,4), use this to index into the 4th dimension of the 5D array.
                q_state_idx = tuple(state) 

                # select best action
                action = np.argmax(q[q_state_idx])
            
            # Perform Action: Performs the selected action and receives the new state, reward, and termination status.
            new_state,reward,terminated,_,_ = env.step(action)

            # Indexing: Prepares indices for accessing and updating the Q-table.
            # Convert state of [1,2,3,4] and action of [1] into (1,2,3,4,1), use this to index into the 5th dimension of the 5D array.
            q_state_action_idx = tuple(state) + (action,)

            # Convert new_state of [1,2,3,4] into (1,2,3,4), use this to index into the 4th dimension of the 5D array.
            q_new_state_idx = tuple(new_state)

            # Q-Table Update: Updates the Q-value for the selected action based on the reward and the maximum Q-value for the new state.
            if is_training:
                q[q_state_action_idx] = q[q_state_action_idx] + learning_rate_a * (
                        reward + discount_factor_g * np.max(q[q_new_state_idx]) - q[q_state_action_idx]
                )

            # State Update: Updates the current state.
            state = new_state

            # Steps Recording: increments the step count, and records the steps taken if the episode has ended.
            step_count+=1
            if terminated:
                steps_per_episode[i] = step_count
                step_count = 0

        # Epsilon Decay: Decreases epsilon by a small amount after each episode to gradually shift from exploration to exploitation.
        epsilon = max(epsilon - 1/episodes, 0)

    # Environment Closure: Closes the environment after all episodes have been completed.
    env.close()

    '''
        Performance Evaluation: Calculates the average steps per episode over the last 100 episodes and plots them. 
        Saves the plot as 'v0_warehouse_solution.png'.
    '''
    sum_steps = np.zeros(episodes)
    for t in range(episodes):
        sum_steps[t] = np.mean(steps_per_episode[max(0, t-100):(t+1)]) # Average steps per 100 episodes
    plt.plot(sum_steps)
    plt.savefig('v0_warehouse_solution.png')

    # Q-Table Saving: If in training mode, saves the final Q-table to a file named 'v0_warehouse_solution.pkl'.
    if is_training:
        f = open("v0_warehouse_solution.pkl","wb")
        pickle.dump(q, f)
        f.close()

# Conditional Execution: Checks if the script is being run directly (not imported as a module).
if __name__ == '__main__':
    
    '''
        Training Phase: Calls the run_q function with 1000 episodes, 
        setting is_training to True to indicate that the agent should be trained. 
        The render parameter is set to False, meaning the environment will not be rendered during training.
    '''
    run_q(1000, is_training=True, render=False)

    '''
        Testing Phase: Calls the run_q function with 1 episode, 
        setting is_training to False to indicate that the agent should be tested. 
        The render parameter is set to True, meaning the environment will be rendered during testing 
        to visually observe the agent's performance.
    '''
    run_q(1, is_training=False, render=True)
