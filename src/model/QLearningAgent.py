import os
import pickle
import random
import numpy as np


class QLearningAgent:
    """
    The QLearningAgent class represents a Q-Learning agent for reinforcement learning.

    Attributes:
        actions (list): The list of possible actions the agent can take.
        learning_rate (float): The learning rate for the Q-Learning algorithm.
        discount_factor (float): The discount factor for the Q-Learning algorithm.
        exploration_rate (float): The exploration rate for the Q-Learning algorithm.
        q_load (str): The path to the file to load the Q-table from.
        q_state (str): The path to the file to load the states from.
        states (list): The list of states the agent has encountered.
        q_table (numpy.ndarray): The Q-table for the Q-Learning algorithm.

    Methods:
        __init__(actions, learning_rate, discount_factor, exploration_rate, q_load, q_state): Initializes the QLearningAgent instance.
        save_table(path): Saves the Q-table to a file.
        load_table(path): Loads the Q-table from a file.
        save_state(path): Saves the states to a file.
        load_state(path): Loads the states from a file.
        choose_action(state): Chooses an action based on the current state.
        update_q_table(state, action, reward, next_state): Updates the Q-table based on the state, action, reward, and next state.
        add_state(state): Adds a state to the list of states and expands the Q-table.
    """

    __slots__ = [
        "actions",
        "learning_rate",
        "discount_factor",
        "exploration_rate",
        "q_load",
        "q_state",
        "states",
        "q_table",
    ]

    def __init__(
        self,
        actions,
        learning_rate=0.01,
        discount_factor=0.9,
        exploration_rate=0.1,
        q_load=None,
        q_state=None,
    ):
        """
        Initializes the QLearningAgent instance.

        Parameters:
            actions (list): The list of possible actions the agent can take.
            learning_rate (float): The learning rate for the Q-Learning algorithm.
            discount_factor (float): The discount factor for the Q-Learning algorithm.
            exploration_rate (float): The exploration rate for the Q-Learning algorithm.
            q_load (str, optional): The path to the file to load the Q-table from. Defaults to "qtable.npy".
            q_state (str, optional): The path to the file to load the states from. Defaults to "qstate.pkl".
        """
        self.actions = actions
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.exploration_rate = exploration_rate

        if q_state is None:
            self.q_state = "qstate.pkl"
            if os.path.isfile(self.q_state):
                self.states = self.load_state(self.q_state)
            else:
                self.states = list()
        else:
            self.states = self.load_state(q_state)
            self.q_state = q_state

        if q_load is None:
            self.q_load = "qtable.npy"
            if os.path.isfile(self.q_load):
                self.q_table = self.load_table(self.q_load)
            else:
                self.q_table = np.zeros((0, len(actions)))
        else:
            self.q_table = self.load_table(q_load)
            self.q_load = q_load

    def save_table(self, path):
        """
        Saves the Q-table to a file.

        Parameters:
            path (str): The path to the file to save the Q-table to.
        """
        np.save(path, self.q_table)

    @staticmethod
    def load_table(path):
        """
        Loads the Q-table from a file.

        Parameters:
            path (str): The path to the file to load the Q-table from.

        Returns:
            numpy.ndarray: The loaded Q-table.
        """
        return np.load(path)

    def save_state(self, path):
        """
        Saves the states to a file.

        Parameters:
            path (str): The path to the file to save the states to.
        """
        with open(path, "wb") as file:
            pickle.dump(self.states, file)

    @staticmethod
    def load_state(path):
        """
        Loads the states from a file.

        Parameters:
            path (str): The path to the file to load the states from.

        Returns:
            list: The loaded states.
        """
        with open(path, "rb") as file:
            return pickle.load(file)

    def choose_action(self, state):
        """
        Chooses an action based on the current state. The action is chosen randomly with a probability of the exploration rate, and the action with the highest Q-value otherwise.

        Parameters:
            state (any): The current state.

        Returns:
            int: The index of the chosen action.
        """
        if state not in self.states:
            self.add_state(state)
        if np.random.uniform(0, 1) < self.exploration_rate:
            choices = self.q_table[self.states.index(state), :].copy()
            possibilities = list()
            for choice in range(len(choices)):
                if choices[choice] >= 0:
                    possibilities.append(choice)
            action = possibilities[random.randint(0, len(possibilities) - 1)]
        else:
            action = np.argmax(
                self.q_table[self.states.index(state), :]
            )  # Exploit learned values
        return action

    def update_q_table(self, state, action, reward, next_state):
        """
        Updates the Q-table based on the state, action, reward, and next state. The Q-value for the state-action pair is updated based on the Q-Learning update rule.

        Parameters:
            state (any): The current state.
            action (int): The index of the action taken.
            reward (float): The reward received.
            next_state (any): The state transitioned to.
        """
        id_state = self.states.index(state)
        if next_state not in self.states:
            self.add_state(next_state)
        id_next_state = self.states.index(next_state)

        old_value = self.q_table[id_state, action]
        next_max = np.max(self.q_table[id_next_state])

        new_value = self.learning_rate * (
            reward + self.discount_factor * next_max - old_value
        )

        self.q_table[id_state, action] += new_value

    def add_state(self, state):
        """
        Adds a state to the list of states and expands the Q-table. The new state is added to the end of the list, and a new row of zeros is added to the Q-table.

        Parameters:
            state (any): The state to add.
        """
        self.states.append(state)
        self.q_table = np.vstack([self.q_table, np.zeros((1, len(self.actions)))])
