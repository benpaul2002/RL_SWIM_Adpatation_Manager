import numpy as np
import json

def initialize_q_values(num_servers, arrival_rate, dimmer_value, response_time, num_actions):
    q_table = np.zeros((num_servers, arrival_rate, dimmer_value, response_time, num_actions))
    with open('q_values.json', 'w') as f:
        json.dump(q_table.tolist(), f)
    return q_table

