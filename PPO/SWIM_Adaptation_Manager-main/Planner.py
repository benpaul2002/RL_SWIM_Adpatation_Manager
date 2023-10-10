_Author_ = "Karthik Vaidhyanathan"

# The class for planning. This uses RL for selecting the actions

from Custom_Logger import logger
from Initializer_Class import Initialize
from Utility_Evaluator import Utility_Evaluator
from Executor import Executor
import json
import datetime
from datetime import datetime
from QLearner import QLearner
import math

'''
Possible actions are adaptation options which include
0. Do nothing
1. Add Server
2. Remove Server
3. increase dimer by 0.1
4. decrease dimer by 0.1
5. Add server and increase dimer by 0.1
6. Add server and decrease dimer by 0.1
7. Remove server and increase dimer by 0.1
8. Remove server and decrease dimer by 0.1
'''

'''
State space is defined as follows:
1. Number of servers in use
2. Arrival rate
3. Dimmer value
4. Response time
'''

class Planner():

    def __init__(self,response_time,server_in_use, arrival_rate,dimmer_value,connection_obj):
        self.response_time = response_time
        self.server_in_use = server_in_use
        self.arrival_rate = arrival_rate
        self.dimmer_value = dimmer_value
        self.connection_obj = connection_obj
        # self.alpha = 0.5
        # self.alpha = 0.9
        self.alpha = 0.5
        # self.alpha = 0.2
        self.gamma = 0.9
        self.epsilon = 0.7
        self.num_actions = 5
        self.learner = QLearner(self.num_actions,self.alpha,self.gamma,self.epsilon)

    def generate_adaptation_plan(self,count,num_iterations):
        # Use the reinforceer to generate the adaptation plan
        logger.info("Inside the planner: Generating the adaptation plan")

        adap_status_json = {}
        with open("adap_status.json", "r") as json_file:
            adap_status_json = json.load(json_file)

        server_add_time_string = adap_status_json["server_added_time"]
        server_count = adap_status_json["current_server_count"]
        server_added_time = datetime.strptime(server_add_time_string, '%Y-%m-%d %H:%M:%S')
        current_time = datetime.now()

        discretized_arrival_rate = 0
        if self.arrival_rate < 10:
            discretized_arrival_rate = 0
        elif self.arrival_rate < 30:
            discretized_arrival_rate = 1
        # to comment
        # elif self.arrival_rate < 60:
        #     discretized_arrival_rate = 2
        # elif self.arrival_rate < 80:
        #     discretized_arrival_rate = 3
        else:
            discretized_arrival_rate = 2

        discretized_response_time = 0
        if self.response_time < 0.5:
            discretized_response_time = 0
        elif self.response_time < 1.0:
            discretized_response_time = 1
        else:
            discretized_response_time = 2

        discretized_dimmer_value = 0
        if self.dimmer_value < 0.3:
            discretized_dimmer_value = 0
        elif self.dimmer_value < 0.6:
            discretized_dimmer_value = 1
        else:
            discretized_dimmer_value = 2

        state = (self.server_in_use,discretized_arrival_rate,discretized_dimmer_value,discretized_response_time)
        action = self.learner.choose_action(state,num_iterations)
        
        execute_obj = Executor(self.dimmer_value,self.server_in_use,self.connection_obj)

        execute_obj.adaptation_executor(action)

        # util_obj = Utility_Evaluator(self.server_in_use, self.arrival_rate, self.dimmer_value)
        # U_rt, U_ct, U_rt_star = util_obj.calculate_utility()
        # reward = U_rt - U_ct # Total utility is the difference between the utility of revenue and the utility of cost
        # next_state = (self.server_in_use,self.arrival_rate,self.dimmer_value,self.response_time)
        # self.learn(state,action,reward,next_state)

        # print (" Adaptation executed ")

        return action

    def learn(self,state,action,reward,next_state, num_iterations):
        
        self.learner.learn(state, action, reward, next_state, num_iterations)
