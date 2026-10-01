import os
import sys
import time

CURRENT = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(CURRENT)
M1 = os.path.join(ROOT, "M1")
if M1 not in sys.path:
    sys.path.insert(0, M1)

from sokoban_map import MapParser
from two_agent_problem import TwoAgentProblem
from agent_algo_1 import AgentAlgorithm1
from agent_algo_2 import AgentAlgorithm2

class DemoHeuristic:
    def evaluate(self, boxes):
        return len(boxes)

def main():
    map_data = MapParser(os.path.join(ROOT, "M1", "example_map.txt"))
    initial_a = map_data.initial_agent
    initial_b = (initial_a[0], initial_a[1] + 1)
    problem = TwoAgentProblem(map_data, initial_a, initial_b, 50)
    state = problem.initial_state

    valid = {"North", "South", "West", "East", "Wait"}
    agents = [
        AgentAlgorithm1(DemoHeuristic(), 1.0),
        AgentAlgorithm2(DemoHeuristic(), 1.0)
    ]

    for number, agent in enumerate(agents, start=1):
        start = time.perf_counter()
        action = agent.choose_action(state, problem)
        elapsed_ms = (time.perf_counter() - start) * 1000
        print("Agent", number, "->", action, "| %.3f ms" % elapsed_ms)
        assert action in valid
        assert elapsed_ms <= 1000.0

if __name__ == "__main__":
    main()