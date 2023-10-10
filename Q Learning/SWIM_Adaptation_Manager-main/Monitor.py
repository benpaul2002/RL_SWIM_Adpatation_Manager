_Author_ = "Karthik Vaidhyanathan"

import socket
from datetime import datetime
from datetime import timedelta
from Initializer_Class import Initialize
from Custom_Logger import logger
import json
import traceback
from Analyzer import Analyzer
from Knowledge import Knowledge
from Utility_Evaluator import Utility_Evaluator
from Planner import Planner
import math


knowledge_obj = Knowledge()

# This is reponsible for continously fetching data from the SWIM simulator

start_adaptation = False
server_add_flag = False
server_remove_flag = False

init_obj = Initialize()
analyzer_obj = Analyzer()

class Monitor():
    
    def continous_monitoring(self):
        # The function continously monitors the data
        logger.info("running the adaptation effector module")
        start_time = datetime.now()
        new_time = datetime.now() + timedelta(minutes=1)
        monitor_dict = {} # This has to be sent to the analyze activity
        old_state={}
        old_action = 0
        new_action = 0

        num_iterations = 0
        while (1):
            new_state = {}
            if (new_time - start_time).seconds >= 60:
                try:
                    # print((new_time - start_time).seconds)
                    print("Number of iterations: ", num_iterations)
                    host = init_obj.host
                    port = init_obj.port  # The same port as used by the server
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    conn = s.connect((host, port))

                    print("Stats: ")

                    s.sendall(b'get_basic_rt')
                    data = s.recv(1024)
                    response_time_base = str(data.decode("utf-8"))

                    s.sendall(b'get_opt_rt')
                    data = s.recv(1024)
                    response_time_opt = str(data.decode("utf-8"))
                    response_time = (float(response_time_base) + float(response_time_opt)) / 2.0
                    print ("Response time ", response_time)
                    monitor_dict["response_time"] = response_time
                    new_state["response_time"] = math.floor(response_time)

                    # Get the arrival rate in the last 60 seconds

                    s.sendall(b'get_arrival_rate')
                    data = s.recv(1024)
                    arrival_rate = float(str(data.decode("utf-8")))
                    monitor_dict["arrival_rate"]  = arrival_rate
                    new_state["arrival_rate"] = math.floor(arrival_rate)
                    print("Arrival rate ", str(arrival_rate))


                    # get the dimmer value
                    s.sendall(b'get_dimmer')
                    data = s.recv(1024)
                    dimmer_value = float(str(data.decode("utf-8")))

                    print ("Current dimmer ", str(dimmer_value))
                    monitor_dict["dimmer_value"] = dimmer_value
                    new_state["dimmer_value"] = math.floor(dimmer_value*10)


                    # Get the active number of servers in the system
                    s.sendall(b'get_active_servers')
                    data = s.recv(1024)
                    server_in_use = int(str(data.decode("utf-8")))
                    monitor_dict["active_servers"] = server_in_use
                    print("Active servers ", str(server_in_use))
                    new_state["active_servers"] = server_in_use
                    s.close()

                    
                    # sending the monitored values to the Analyzer class

                    # the knowledge object will be the connection object inside analyzer
                    # check if old state is not empty
                    if len(old_state) != 0:
                        util_obj = Utility_Evaluator()
                        U_rt, U_ct, U_rt_star = util_obj.calculate_utility(old_state['active_servers'], old_state['response_time'], old_state['dimmer_value'])
                        # reward = U_rt - U_ct # Total utility is the difference between the utility of revenue and the utility of cost
                        # print("Revenue: ", U_rt)
                        # print("Cost: ", U_ct)
                        reward = 0

                        # # ----------------------------------------------------
                        # if response_time > 1:
                        #     print("Response time too high - penalizing ", 50*(math.floor(response_time)))
                        #     reward -= 50*(math.floor(response_time))
                        # elif response_time > 0.5:
                        #     print("Response time slightly high - penalizing ", 10*(math.floor(response_time)))
                        #     reward -= 10*(math.floor(response_time))
                        # elif response_time < 2:
                        #     if response_time < 0.1 and server_in_use > 1:
                        #         print("Too many servers - penalizing")
                        #         reward -= 500               # completely unnecessary since response time is already pretty good - why more than one server?
                        #     elif response_time < 0.3 and server_in_use > 2:
                        #         print("Too many servers - penalizing")
                        #         reward -= 500
                        #     else: 
                        #         print("Response time low - rewarding")
                        #         reward += 600
                                
                        # # ----------------------------------------------------
                        # if dimmer_value < 0.2:
                        #     print("Dimmer value below 0.2 - penalizing 100")
                        #     reward -= 400
                        # elif dimmer_value < 0.5:
                        #     print("Dimmer value between 0.2 and 0.5 - penalizing 50")
                        #     reward -= 150
                        # elif dimmer_value < 0.8:
                        #     print("Dimmer value between 0.5 and 0.8 - rewarding 50")
                        #     reward += 200
                        # else:
                        #     print("Dimmer value above 0.8 - rewarding 100")
                        #     reward += 400
                        # # ----------------------------------------------------

                        # new conditions

                        if(server_in_use == 1 and response_time < 2 and dimmer_value >= 0.7):
                            reward = 1000
                        elif(server_in_use == 1 and response_time < 2 and dimmer_value < 0.7):
                            reward = 500*(dimmer_value)
                        elif(server_in_use == 1 and response_time >= 2 and dimmer_value >= 0.7):
                            reward = -200*(response_time*2)
                        elif(server_in_use == 1 and response_time >= 2 and dimmer_value < 0.7):
                            reward = -500*(response_time*2) - 500*(1/(dimmer_value+0.1))
                        elif(server_in_use == 2 and response_time < 2 and dimmer_value >= 0.7):
                            reward = 700
                        elif(server_in_use == 2 and response_time < 2 and dimmer_value < 0.7):
                            reward = 200*(dimmer_value)
                        elif(server_in_use == 2 and response_time >= 2 and dimmer_value >= 0.7):
                            reward = -700*(response_time*2)
                        elif(server_in_use == 2 and response_time >= 2 and dimmer_value < 0.7):
                            reward = -600*(response_time*2) - 600*(1/(dimmer_value+0.1))
                        elif(server_in_use == 3 and response_time < 2 and dimmer_value >= 0.7):
                            reward = 400
                        elif(server_in_use == 3 and response_time < 2 and dimmer_value < 0.7):
                            reward = 100*(dimmer_value)
                        elif(server_in_use == 3 and response_time >= 2 and dimmer_value >= 0.7):
                            reward = -1200*(response_time*2)
                        elif(server_in_use == 3 and response_time >= 2 and dimmer_value < 0.7):
                            reward = -750*(response_time*2) - 750*(1/(dimmer_value+0.1))

                        # to try
                        if(dimmer_value<0.2):
                            reward = -1000

                        # newer conditions - trial

                        # resp_reward = 0
                        # if response_time < 1:
                        #     resp_reward = 1000/server_in_use
                        # else:
                        #     resp_reward = -50*response_time

                        # dim_reward = 0
                        # if dimmer_value > 0.65:
                        #     dim_reward = (dimmer_value-0.65)*2000  # 0 - 700
                        # else:
                        #     dim_reward = -2000*(0.65-dimmer_value)  # -1300 - 0 

                        # server_reward = 0
                        # if server_in_use == 1:
                        #     server_reward = 300
                        # elif server_in_use == 2:
                        #     server_reward = 0
                        # else:
                        #     server_reward = -300

                        # reward = resp_reward + dim_reward
                        
                        print("Reward ", reward)
                        plan_obj = Planner(old_state['response_time'], old_state['active_servers'], old_state["arrival_rate"], old_state["dimmer_value"], conn)
                        # print("Updating Q values")
                        plan_obj.learn(old_state,old_action,reward,new_state, num_iterations)

                    old_state = new_state

                    # if new_action:
                    old_action = new_action
                    new_action = analyzer_obj.perform_analysis(monitor_dict,conn,num_iterations) # This will pass the control to the next class

                    print("----------------------------------------------")
                    print()

                except Exception as e:
                    logger.error(e)
                    traceback.print_exc()

                start_time = datetime.now()

                num_iterations += 1

            new_time = datetime.now()

if __name__ == '__main__':
    monitor_obj = Monitor()
    monitor_obj.continous_monitoring()