import numpy as np
import json
import os
# from InitializeQValues import initialize_q_values

Q_VALUES_FILE_NAME = './Q_folder/1-q_values.json'


class QLearner:
    def __init__(self, num_actions, alpha=0.5, gamma=0.9, epsilon=0.1):
        # self.num_servers = num_servers
        # self.arrival_rate = arrival_rate
        # self.dimmer_value = dimmer_value
        # self.response_time = response_time
        self.num_actions = num_actions
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon

        if os.path.exists(Q_VALUES_FILE_NAME):
            with open(Q_VALUES_FILE_NAME, 'r') as f:
                self.q_table = np.array(json.load(f))
        else:
            self.initialize_q_values(4, 5, 11, 3, 9)
            print("Initialized")
            print(self.q_table.shape)
    
    def initialize_q_values(self, num_servers, arrival_rate, dimmer_value, response_time, num_actions):
        self.q_table = np.zeros((num_servers, arrival_rate, dimmer_value, response_time, num_actions))
        with open(Q_VALUES_FILE_NAME, 'w') as f:
            json.dump(self.q_table.tolist(), f)
        # return q_table

    def choose_action(self, state, num_iterations):
        print("Number of iterations: ", num_iterations)
        server_in_use = state[0]
        arrival_rate = state[1]
        dimmer_value = state[2]
        response_time = state[3]
        
        if np.random.uniform() < self.epsilon * (9-(num_iterations/10)):
            print("Exploring: Epsilon: ", self.epsilon * (9-(num_iterations/10)))
            action = np.random.choice(self.num_actions)
        else:
            print("Exploiting: Epsilon: ", self.epsilon * (9-(num_iterations/10)))
            print(state)
            q_values = self.q_table[server_in_use][arrival_rate][dimmer_value][response_time]
            action = np.argmax(q_values)
        return action

    def update_q_value(self, state, action, reward, next_state):
        print("State: (Server in use, Arrival rate, Dimmer value, Response time)")
        print(state)
        print("Next State: (Server in use, Arrival rate, Dimmer value, Response time)")
        print(next_state)
        cur_server_in_use = state[0]
        cur_arrival_rate = state[1]
        cur_dimmer_value = state[2]
        cur_response_time = state[3]

        next_server_in_use = next_state[0]
        next_arrival_rate = next_state[1]
        next_dimmer_value = next_state[2]
        next_response_time = next_state[3]


        discretized_old_arrival_rate = 0
        if cur_arrival_rate < 10:
            discretized_old_arrival_rate = 0
        elif cur_arrival_rate < 30:
            discretized_old_arrival_rate = 1
        elif cur_arrival_rate < 60:
            discretized_old_arrival_rate = 2
        elif cur_arrival_rate < 80:
            discretized_old_arrival_rate = 3
        else:
            discretized_old_arrival_rate = 4

        discretized_old_response_time = 0
        if cur_response_time < 0.5:
            discretized_old_response_time = 0
        elif cur_response_time < 1.0:
            discretized_old_response_time = 1
        else:
            discretized_old_response_time = 2

        discretized_new_arrival_rate = 0
        if next_arrival_rate < 10:
            discretized_new_arrival_rate = 0
        elif next_arrival_rate < 30:
            discretized_new_arrival_rate = 1
        elif next_arrival_rate < 60:
            discretized_new_arrival_rate = 2
        elif next_arrival_rate < 80:
            discretized_new_arrival_rate = 3
        else:
            discretized_new_arrival_rate = 4

        discretized_new_response_time = 0
        if next_response_time < 0.5:
            discretized_new_response_time = 0
        elif next_response_time < 1.0:
            discretized_new_response_time = 1
        else:
            discretized_new_response_time = 2

        q_value = self.q_table[cur_server_in_use][discretized_old_arrival_rate][cur_dimmer_value][discretized_old_response_time][action]
        max_q_value_next_state = np.max(self.q_table[next_server_in_use][discretized_new_arrival_rate][next_dimmer_value][discretized_new_response_time])
        new_q_value = q_value + self.alpha * (reward + self.gamma * max_q_value_next_state - q_value)
        self.q_table[cur_server_in_use][discretized_old_arrival_rate][cur_dimmer_value][discretized_old_response_time][action] = new_q_value

        # Save updated q_table to file
        with open(Q_VALUES_FILE_NAME, 'w') as f:
            json.dump(self.q_table.tolist(), f)

    def learn(self, state, action, reward, next_state):
        state_dict = state
        state = (state_dict['active_servers'], state_dict['arrival_rate'],
                 state_dict['dimmer_value'], state_dict['response_time'])
        next_state_dict = next_state
        next_state = (next_state_dict['active_servers'], next_state_dict['arrival_rate'],
                      next_state_dict['dimmer_value'], next_state_dict['response_time'])
        self.update_q_value(state, action, reward, next_state)
