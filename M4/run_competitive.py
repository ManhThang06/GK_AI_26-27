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

class TemporaryHeuristic:
    def evaluate(self, boxes):
        return len(boxes)

def main():
    map_file = os.path.join(ROOT, "M1", "example_map.txt")
    map_data = MapParser(map_file)
    initial_a = map_data.initial_agent
    initial_b = (initial_a[0], initial_a[1] + 1)
    problem = TwoAgentProblem(map_data, initial_a, initial_b, n_steps=50)
    heuristic = TemporaryHeuristic()
    agent_a = AgentAlgorithm1(heuristic=heuristic, time_limit=1.0)
    agent_b = AgentAlgorithm2(heuristic=heuristic, time_limit=1.0)
    app = TwoAgentCompetitiveApp(problem, agent_a, agent_b)
    app.run()
if __name__ == "__main__":
    main()