# Self Adaptive Software Systems using Reinforcement Learning

We use SWIM web system exemplar to simulate network traffic. The goal is simple - to ensure good user experience and low costs. To achieve this, we dynamically change the active number of servers and the dimmer value (value between 0 and 1 which is a measure of how graphically intensive the system is). So, our goal boils down to this - 

1. minimize server cost
2. minimize response time
3. maximize dimmer value

To achieve this, we use Proximal Policy Optimization, a popular RL algorithm by OpenAI. Our current results occasionally meet the baseline results. However, with further training, we believe beating the baseline is possible.

# Steps to run

1. Clone the repo and go into the swim_rl_IS/PPO/gymie/ directory.
2. Start SWIM - 
    1. If you do not have SWIM installed, follow this [guide](https://github.com/karthikv1392/swim) before proceeding.
    2. Once you have SWIM installed, run it using `sudo docker start swim`.
    3. Open [http://localhost:6901](http://localhost:6901/) on your browser and enter `vncpassword` as the password.
    4. Click on the Applications button on the top left corner and open the terminal emulator.
    5. Run `cd ~/seams-swim/swim/simulations/swim/`.
    6. Run `./run.sh sim 1`.
3. Run `python stableppo.py` on your local terminal (in the /gymie directory).
    
    The simulator and program should now be running. Your local terminal will be updated every 60s with updated information, including current stats and action taken. 
    
4. Once the simulation has completed, you can generate a graph to visualize the performance results. To do so, run the following commands in the SWIM terminal - 
    1.  `cd ~/seams-swim/results` 
    2. `../swim/tools/plotResults.sh SWIM sim 1 plot.png`

Alternatively, you can run `sudo ./scripty.sh` from your local terminal in the gymie directory. This script will automatically start swim, run the code, and save the results in your local machine. We encourage the use of this method since it’s far more convenient. 

# Modifications

There are several modifications you can make in SWIM. Some of the common modifications you might need to make are listed below -  

### Changing the trace file

The trace file is a file containing several timestamps. This is the file that SWIM uses to simulate network traffic. If you wish to change the trace file being used, follow the steps below - 

1. Navigate to `~/seams-swim/swim/simulations/swim/` in the SWIM terminal. 
2. Run `vi swim.ini`. 
3. Scroll down till you see the # simulation input and duration comment. Change the name of the .delta file in the following line with the name of the file that you wish to use. You can navigate to `~/seams-swim/swim/simulations/swim/traces/` to check alternative trace files to use. Additionally, if you wish to use your own trace file, add them to this folder and follow the same steps as above.
    
    Note that if the new trace file duration is different from the original file, you will have to change the simulation length. To find the duration of a trace file, simply sum up all the values in the file.
    

### Changing the simulation length

1. Navigate to `~/seams-swim/swim/simulations/swim/` in the SWIM terminal. 
2. Run `vi swim.ini`. 
3. Scroll down till you see the # simulation input and duration comment. A couple lines below this comment, you can find the sim-time-limit field. Change the value here to the duration of the trace file you are using. We recommend changing the warmup-period field as well, so that a reasonable proportion between the sim-time-limit and warmup-period is maintained (6300:900). This doesn’t need to exact.

We will add in details for other modifications as we update our code to handle more general cases.
