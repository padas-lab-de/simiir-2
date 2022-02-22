import numpy as np
import itertools
from numpy.random import choice
from itertools import tee, islice, chain
import pickle

class MarkovChain(object): 
    def __init__(self, transition_matrix, states, model_type):
        """
        Initialize the MarkovChain instance.
 
        Parameters
        ----------
        transition_matrix: 2-D array
            A 2-D array representing the probabilities of change of 
            state in the Markov Chain.
 
        states: 1-D array 
            An array representing the states of the Markov Chain. It
            needs to be in the same order as transition_matrix.
        """
        if transition_matrix:
            with open(transition_matrix, 'rb') as f:
                self.transition_matrix = pickle.load(f)
        else:
           self.transition_matrix = np.atleast_2d(transition_matrix)

        if states:
            with open(states, 'rb') as f:
                self.states = pickle.load(f)
        else:
            self.states = states
            
        self.model_type = model_type
        self.index_dict = {self.states[index]: index for index in 
                           range(len(self.states))}
        self.state_dict = {index: self.states[index] for index in
                           range(len(self.states))}

    def get_model_type(self):
        return self.model_type
    
    def next_state(self, current_state):
        """
        Returns the state of the random variable at the next time 
        instance.
 
        Parameters
        ----------
        current_state: str
            The current state of the system.
        """
        return np.random.choice( self.states, p=self.transition_matrix[self.index_dict[current_state], :])

    def generate_states(self, current_state, no=10):
        """
        Generates the next states of the system.
 
        Parameters
        ----------
        current_state: str
            The state of the current random variable.
 
        no: int
            The number of future states to generate.
        """
        future_states = []
        future_states.append(current_state)
        for i in range(no):
            next_state = self.next_state(current_state)
            future_states.append(next_state)
            current_state = next_state
        return future_states
