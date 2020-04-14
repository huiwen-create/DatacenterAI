from keras.layers import Input, Dense, Dropout, BatchNormalization
from keras.models import Model, Sequential
from keras.optimizers import Adam
import numpy as np
from collections import deque


# BUILDING THE BRAIN
class Brain():
    
    def __init__ (self, learning_rate = 0.001, number_actions = 5, number_states = 3, loss = 'mean_squared_error', optimizer = Adam()):
        
        self.learning_rate = learning_rate 
        
        # Input layer
        states = Input(shape = (number_states,))
        
        # Hidden layers
        x = Dense(units = 64, activation = 'relu', kernel_initializer='he_normal', bias_initializer='zeros')(states)
        x = Dropout(rate = 0.1)(x)
     
        y = Dense(units = 64, activation = 'relu', kernel_initializer='he_normal', bias_initializer='zeros')(x)
        y = Dropout(rate = 0.1)(y)
        
        # Output layer
        q_values = Dense(units = number_actions, activation = 'linear', kernel_initializer='he_normal', bias_initializer='zeros')(y)
        # q_values = Dense(units = number_actions, activation = 'tanh')(y)
        # q_values = Dense(units = number_actions, activation = 'softmax')(y)

        # Assembling the full architecture in a model object (object variable)
        self.model = Model(inputs = states, outputs = q_values)
        
        # Compiling the model with loss and optimizer (applying the compile method)
        self.model.compile(loss = loss, optimizer = optimizer)



# DEEP Q-LEARNING ALGORITHM (With Experience Replay)
class DQN():
    
    def __init__(self, max_memory = 100, discount = 0.99):
        self.memory = deque(maxlen=max_memory)
        self.max_memory = max_memory
        self.discount = discount
    
    # Methods to build the memory in Experience Replay
    def remember(self, transition, game_over):
        self.memory.append([transition, game_over])
   
    # Methods to build two batches of 10 In and 10 Targes by extracting 10 transition
    def get_batch(self, model, batch_size, r_hat):
        len_memory = len(self.memory)
        num_inputs = self.memory[0][0][0].shape[1]
        num_outputs = model.output_shape[-1]
        inputs = np.zeros((min(len_memory, batch_size), num_inputs))
        targets = np.zeros((min(len_memory, batch_size), num_outputs))
        for i, idx in enumerate(np.random.randint(0, len_memory, size = min(len_memory, batch_size))):
            current_state, action, reward, next_state, r_hat_i = self.memory[idx][0]
            game_over = self.memory[idx][1]
            inputs[i] = current_state
            targets[i] = model.predict(current_state)[0]
            Q_sa_next = np.max(model.predict(next_state)[0])   
            if game_over:
                targets[i, action] = reward - r_hat
                # targets[i, action] = reward 
            else:
                targets[i, action] = reward - r_hat + self.discount * Q_sa_next
                # targets[i, action] = reward + self.discount * Q_sa_next
        return inputs, targets

