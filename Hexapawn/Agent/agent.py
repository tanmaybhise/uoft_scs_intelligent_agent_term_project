import sys
sys.path.append("d:/Projects/uoft_scs_project/Hexapawn")

import os
os.chdir("D:/Projects/uoft_scs_project/Hexapawn")
import json
from json.decoder import JSONDecodeError

from Environment.environment import Hexapawn
from Config.config import Config
import random
import copy
import pandas as pd

import logging

class Agent():
    def __init__(self, env, whoami="W", type="logical"):
        self.env = env
        self.whoami = whoami
        self.type = type
        self.actions = env.get_actions()
        self.state = env.state
        self.total_reward = 0
        self.steps_played = 0
        if os.path.isfile(Config.agent_state_memory_path):
            try:
                self.agent_state_memory = json.load(open(Config.agent_state_memory_path, 'r'))
            except JSONDecodeError:
                self.agent_state_memory = {}
        else:
            self.agent_state_memory = {}

        if self.type == "logical":
            if os.path.isfile(Config.q_table_path):
                self.q_table = pd.read_csv(Config.q_table_path, index_col=[0])
            else:
                self.q_table = pd.DataFrame()
                self.q_table.index.name = "state_key"

    def run_logical_model(self):
        logging.info("Running logical agent")
        try:
            if random.uniform(0,1) < Config.logical_agent_epsilon:
                agent_pawn_locations = self.get_agent_pawn_locations()
                q_table_columns = []
                for loc in agent_pawn_locations:
                    q_table_columns+=list(self.q_table.columns[self.q_table.columns.str.contains(str(loc))])
                q_table = self.q_table[q_table_columns]
                state = self.agent_state_memory[str(self.state['board'])]
                optimal_action = q_table.loc[state].idxmax().split("_")
                start, action = eval(optimal_action[0]), optimal_action[1]
            else:
                start, action = self.run_naive_model()
        except KeyError:
            start, action = self.run_naive_model()

        return start, action
    
    def run_naive_model(self):
        logging.info("Running naive agent")
        start = random.choice(self.get_agent_pawn_locations())
        action = random.choice(list(self.actions.keys()))
        return start, action

    def step(self):
        self.previous_state = copy.deepcopy(self.state)
        if not self.env.state['terminated']:
            while self.env.whose_turn == self.whoami:
                if self.type == "logical":
                    start, action = self.run_logical_model()
                elif self.type == "naive":
                    start, action = self.run_naive_model()
                end = self.get_end_for_action(start, action)
                self.state = self.env.make_move(start, end)
                self.total_reward+=self.state['reward']
                self.update_agent_state_memory()
                if self.type == "logical":
                    self.update_q_table(start, action, self.state['reward'])
                self.steps_played+=1

        if self.type == "logical":
            self.q_table.fillna(0).to_csv(Config.q_table_path)
        json.dump(self.agent_state_memory, open(Config.agent_state_memory_path, 'w'))

    def get_agent_pawn_locations(self):
        agent_pawns = []
        for i in range(len(self.state['board'])):
            for j in range(len(self.state['board'][0])):
                if self.state['board'][i][j] == self.whoami:
                    agent_pawns.append((i,j))
        return agent_pawns

    def get_end_for_action(self, start, action):
        if action == "forward":
            if self.whoami=="W":
                return ((start[0]+1), start[1])
            else:
                return ((start[0]-1), start[1])
        if action=="diagonal1":
            if self.whoami=="W":
                return ((start[0]+1), start[1]+1)
            else:
                return ((start[0]-1), start[1]+1)
        if action=="diagonal2":
            if self.whoami=="W":
                return ((start[0]+1), start[1]-1)
            else:
                return ((start[0]-1), start[1]-1)
            
    def update_agent_state_memory(self):
        state_key = str(self.state['board'])
        if len(self.agent_state_memory.items()) == 0:
            self.agent_state_memory[state_key] = 0
        elif state_key not in self.agent_state_memory:
            self.agent_state_memory[state_key] = max(self.agent_state_memory.values()) + 1

        state_key = str(self.previous_state['board'])
        if len(self.agent_state_memory.items()) == 0:
            self.agent_state_memory[state_key] = 0
        elif state_key not in self.agent_state_memory:
            self.agent_state_memory[state_key] = max(self.agent_state_memory.values()) + 1

    def update_q_table(self, start, action, reward):
        state_key = str(self.previous_state["board"])
        next_state_key = str(self.state["board"])

        next_state_index = self.agent_state_memory[next_state_key]
        state_index = self.agent_state_memory[state_key]

        if str(start)+"_"+str(action) in self.q_table.columns:
            try:
                max_q = self.q_table.loc[next_state_index, self.q_table.columns[self.q_table.columns.str.contains(str(start))]].max()
            except KeyError:
                max_q = 0
            try:
                current_q = self.q_table.loc[state_index, str(start)+"_"+str(action)]
            except KeyError:
                current_q = 0
            updated_q = current_q + Config.logical_agent_alpha * (reward + Config.logical_agent_gamma * (max_q) - current_q)
            self.q_table.loc[state_index, str(start)+"_"+str(action)] = updated_q
        else:
            self.q_table.loc[state_index, str(start)+"_"+str(action)] = 0

if __name__=="__main__":
    env = Hexapawn()
    agent = Agent(env, "W")
    agent.env.make_move((0,0), (1,0))
    agent.env.print_board()
    

