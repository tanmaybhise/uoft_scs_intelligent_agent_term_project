import sys
sys.path.append("d:/Projects/uoft_scs_project/Hexapawn")

import os
os.chdir("D:/Projects/uoft_scs_project/Hexapawn")

from Config.config import Config
from Environment.environment import Hexapawn
from Agent.agent import Agent

import numpy as np
import pandas as pd

import logging
logging.basicConfig(level=logging.CRITICAL)

import warnings
warnings.filterwarnings("ignore")


class MultiAgent():
    def __init__(self, agentW_type="logical", agentB_type="naive"):
        self.agentW_type = agentW_type
        self.agentB_type = agentB_type

    def run_episode(self):
        self.env = Hexapawn()
        self.agentW = Agent(self.env, "W", type=self.agentW_type)
        self.agentB = Agent(self.env, "B", type=self.agentB_type)

        while not self.env.state['terminated']:
            self.agentW.step()
            self.agentB.step()
        self.update_reward_history()
        
    def update_reward_history(self):
        
        if os.path.isfile(Config.agent_reward_history_path):
            reward_history = pd.read_csv(Config.agent_reward_history_path, index_col=[0])
            episode_number = str(max([int(inx.split("_")[0]) for inx in reward_history.index]) + 1)
        else:
            reward_history = pd.DataFrame()
            reward_history.index.name = "episode"
            episode_number = "0"
        
        reward_history.loc[episode_number+"_W", 'player'] = "W"
        reward_history.loc[episode_number+"_W", 'total_reward'] = self.agentW.total_reward
        reward_history.loc[episode_number+"_W", 'steps_played'] = self.agentW.steps_played
        reward_history.loc[episode_number+"_W", 'won'] = ["W", "B"][np.argmax([self.agentW.total_reward, self.agentB.total_reward])]
        
        reward_history.loc[episode_number+"_B", 'player'] = "B"
        reward_history.loc[episode_number+"_B", 'total_reward'] = self.agentB.total_reward
        reward_history.loc[episode_number+"_B", 'steps_played'] = self.agentB.steps_played
        reward_history.loc[episode_number+"_B", 'won'] = ["W", "B"][np.argmax([self.agentW.total_reward, self.agentB.total_reward])]

        reward_history.to_csv(Config.agent_reward_history_path)

if __name__=="__main__":
    agents = MultiAgent(agentW_type="logical", agentB_type="naive")

    W,B,N=0,0,100
    for _ in range(N):
        agents.run_episode()
        if agents.agentW.total_reward > agents.agentB.total_reward:
            W+=1
        else:
            B+=1

    print(f"Agent W winning percent: {W/N}")
    print(f"Agent B winning percent: {B/N}")