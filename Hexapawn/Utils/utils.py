import os
os.chdir("D:/Projects/uoft_scs_project/Hexapawn")
import sys

from Config.config import Config
import matplotlib.pyplot as plt
import seaborn as sns

import numpy as np
import pandas as pd

def plot_logical_agent_win_percent(window_size=10, last_n_episodes = None):
    reward_history = pd.read_csv(Config.agent_reward_history_path, index_col=[0])
    reward_history = reward_history.reset_index()
    reward_history['episode_no'] = reward_history['episode'].apply(lambda x: int(x.split("_")[0]))
    reward_history = reward_history.drop_duplicates(subset=["episode_no"]).reset_index(drop=True)
    if last_n_episodes is not None:
        reward_history = reward_history.sort_values(by="episode_no").tail(last_n_episodes).reset_index(drop=True)

    win_percent = []
    chunks = np.array_split(reward_history, reward_history.shape[0]//window_size)
    for chunk in chunks:
        if chunk.shape[0] == window_size:
            win_percent.append((chunk['won'].value_counts()/window_size)["W"])

    sns.lineplot(win_percent)
    plt.title("Player W winning percentage (Logical Agent)")
    plt.xlabel("Evaluation Point")
    plt.ylabel("Win %")

    return win_percent