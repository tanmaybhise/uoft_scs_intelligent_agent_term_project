class Config:
    agent_state_memory_path = "./Agent/memory/agent_state_memory.json"
    agent_reward_history_path = "./Agent/memory/reward_history.csv"
    q_table_path = "./Agent/memory/q_table.csv"
    logical_agent_alpha = 0.1
    logical_agent_gamma = 0.5
    logical_agent_epsilon = 0.9