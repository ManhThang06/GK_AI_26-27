import importlib.util
import os
import sys

CURRENT = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(CURRENT)
M1 = os.path.join(ROOT, "M1")
if M1 not in sys.path:
    sys.path.insert(0, M1)

from sokoban_map import MapParser
from two_agent_problem import TwoAgentProblem
from agent_algo_1 import AgentAlgorithm1
from agent_algo_2 import AgentAlgorithm2
from gui.two_agent_competitive_app import TwoAgentCompetitiveApp

def load_req2_heuristic(map_file, goals):
    module_path = os.path.join(ROOT, "M2", "ucs&a_.py")
    spec = importlib.util.spec_from_file_location("req2_ucs_astar", module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    with open(map_file, "r", encoding="utf-8") as f:
        lines = [line.rstrip("\n\r") for line in f]
    if not lines:
        raise ValueError("Map rong.")
    max_cols = max(len(line) for line in lines)
    board_matrix = []

    for line in lines:
        row = list(line)
        if len(row) < max_cols:
            row.extend(["%"] * (max_cols - len(row)))
        board_matrix.append(row)
    return module.SokobanHeuristic(board_matrix, goals)

def main():
    map_file = os.path.join(ROOT, "M4", "competitive_map.txt")
    map_data = MapParser(map_file)
    initial_a = map_data.initial_agent
    directions = [
        (-1, 0), 
        (1, 0),    
        (0, -1),   
        (0, 1)     
    ]
    initial_b = None
    for dr, dc in directions:
        pos = (initial_a[0] + dr, initial_a[1] + dc)
        if (pos not in map_data.walls and pos not in map_data.initial_boxes and pos != initial_a):
            initial_b = pos
            break
    if initial_b is None:
        raise ValueError("Khong tim thay vi tri hop le cho Agent B")
        
    problem = TwoAgentProblem(map_data, initial_a, initial_b, n_steps=100)
    heuristic = load_req2_heuristic(map_file, problem.goals)
    agent_a = AgentAlgorithm1(heuristic=heuristic, time_limit=0.90)
    agent_b = AgentAlgorithm2(heuristic=heuristic, time_limit=0.90)
    app = TwoAgentCompetitiveApp(problem, agent_a, agent_b)
    app.run()

if __name__ == "__main__":
    main()