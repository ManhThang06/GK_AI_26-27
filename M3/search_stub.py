import heapq
import itertools


def ucs(problem):
    counter = itertools.count()
    frontier = [(0, next(counter), problem.initial_state, [])]
    explored = set()
    max_frontier = 1
    expanded = 0

    while frontier:
        cost, _, state, path = heapq.heappop(frontier)

        if problem.goal_test(state):
            return path, cost, expanded, max_frontier

        if state in explored:
            continue
        explored.add(state)
        expanded += 1

        for action in problem.actions(state):
            new_state = problem.result(state, action)
            if new_state not in explored:
                new_cost = cost + problem.step_cost(state, action)
                heapq.heappush(frontier, (new_cost, next(counter), new_state, path + [action]))

        max_frontier = max(max_frontier, len(frontier))

    return None, None, expanded, max_frontier


def astar(problem, heuristic):
    counter = itertools.count()
    h0 = heuristic(problem.initial_state, problem)
    frontier = [(h0, 0, next(counter), problem.initial_state, [])]
    explored = set()
    max_frontier = 1
    expanded = 0

    while frontier:
        f, g, _, state, path = heapq.heappop(frontier)

        if problem.goal_test(state):
            return path, g, expanded, max_frontier

        if state in explored:
            continue
        explored.add(state)
        expanded += 1

        for action in problem.actions(state):
            new_state = problem.result(state, action)
            if new_state not in explored:
                new_g = g + problem.step_cost(state, action)
                new_f = new_g + heuristic(new_state, problem)
                heapq.heappush(frontier, (new_f, new_g, next(counter), new_state, path + [action]))

        max_frontier = max(max_frontier, len(frontier))

    return None, None, expanded, max_frontier