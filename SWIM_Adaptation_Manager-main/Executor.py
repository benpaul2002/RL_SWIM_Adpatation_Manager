_Author_ = "Karthik Vaidhyanathan"

from Custom_Logger import logger
from Initializer_Class import Initialize
import socket


init_obj = Initialize()
from datetime import datetime
import json

# Executes the adaptation on the system based on the selected action



class Executor():
    def __init__(self,dimmer_value,server_in_use,conn_obj):
        self.host = init_obj.host
        self.port = init_obj.port
        self.dimmer_value=dimmer_value
        self.server_in_use = server_in_use
        self.conn_obj = conn_obj

    def add_server(self):
        if(self.server_in_use == 3): 
            return
        
        logger.info("inside add server module")
        # To add server in swim
        print (" Adding Server ")
        host = self.host
        port = self.port  # The same port as used by the server
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            conn = s.connect((host, port))
            s.sendall(b'add_server')
            data = s.recv(1024)
            s.close()
            print(str(data.decode("utf-8")))
            server_add_flag = True
            server_add_time = datetime.now() # This will be the time when a server has been added
            server_add_time_string = server_add_time.strftime('%Y-%m-%d %H:%M:%S')
            server_count = self.server_in_use + 1

            server_json = {}

            server_json["current_server_count"] = server_count
            server_json["server_added_time"] = server_add_time_string

            # Writing the current JSON status
            with open ("adap_status.json","w") as json_file:
                json.dump(server_json,json_file)
            json_file.close()

            #self.conn_obj.create_adaptation_record(server_add_time,server_add_flag,False,"add_server")
            # add details to database
            logger.info("Server added successfully")
        except Exception as e:
            logger.error(e)

    def change_dimmer(self, change_flag):
        # change flag can be increase or decrease
        if(self.dimmer_value == 1.0 and change_flag == "increase"):
            return
        if(self.dimmer_value == 0.0 and change_flag == "decrease"):
            return
        logger.info("inside change dimer module, change flag " + str(change_flag))
        print("Changing dimer ", change_flag)
        host = init_obj.host
        port = init_obj.port  # The same port as used by the server
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            conn = s.connect((host, port))
            value = "0.25"
            if change_flag == "increase":
                value = str(float(self.dimmer_value) + 0.1)
            elif change_flag == "decrease":
                value = str(float(self.dimmer_value) - 0.1)

            value = str.encode(value)
            s.sendall(b'set_dimmer ' + value)
            data = s.recv(1024)
            print (" dimmer status ")
            print(str(data.decode("utf-8")))
            s.close()
        except Exception as e:
            logger.error(e)




    def remove_server(self):
        if(self.server_in_use == 1):
            return
        
        logger.info("removing server")
        # To remove server in swim
        print (" Removing Server ")
        host = self.host
        port = self.port  # The same port as used by the server

        '''
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        conn = s.connect((host, port))
        s.sendall(b'get_active_servers')
        data = s.recv(1024)
        server_count = str(data.decode("utf-8"))
        print (server_count)
        '''

        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            conn = s.connect((host, port))


            s.sendall(b'remove_server')
            data = s.recv(1024)
            s.close()
            server_count = self.server_in_use - 1
            server_json = {}

            # load the adap_statu.json file get the server count and the time string and add them back by updating the count

            with open("adap_status.json", "r") as json_file:
                server_json = json.load(json_file)

            server_json["current_server_count"] = server_count

            # Writing the current JSON status
            with open("adap_status.json", "w") as json_file:
                json.dump(server_json, json_file)
            json_file.close()
            print(str(data.decode("utf-8")))
            self.server_remove_flag = True
            self.server_remove_time = datetime.now()
            logger.info("server removed successfully")
        except Exception as e:
            print (e)
            logger.error(e)



    def adaptation_executor(self,action):
        if action == 0:
            logger.info("No adaptation required")
            print (" No adaptation required ")
            return "success"
        # no action will be automatically taken care
        logger.info("Inside the Executor: executing the adaptations")
        if action == 1:
            #Add server first check if the server is already full
            if self.server_in_use == 3:
                print("Tried adding server but hit server limit")
                return "success"
            
            self.add_server()
            self.strategy = [["add_server",1.0,60.0]]
            print("Adding server")
        elif action == 2:
            # Remove a server
            self.remove_server()
            self.strategy = [["remove_server", 1.0,-1.0]]
            print("Removing server")

        elif action == 3:
            self.change_dimmer("increase")
            print("Increasing dimmer")
        elif action == 4:
            self.change_dimmer("decrease")
            print("Decreasing dimmer")

        elif action == 5:
            if self.server_in_use == 3:
                print("Tried adding server but hit server limit")
                return "success"
            self.add_server()
            self.change_dimmer("increase")
            print("Adding server and increasing dimmer")

        elif action == 6:
            if self.server_in_use == 3:
                print("Tried adding server but hit server limit")
                return "success"
            self.add_server()
            self.change_dimmer("decrease")
            print("Adding server and decreasing dimmer")

        elif action ==  7:
            self.remove_server()
            self.change_dimmer("increase")
            print("Removing server and increasing dimmer")

        elif action == 8:
            self.remove_server()
            self.change_dimmer("decrease")
            print("Removing server and decreasing dimmer")

        print (" Executed the adaptation ")
        return "success"
