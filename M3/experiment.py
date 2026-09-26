import time

from engine_stub import SokobanProblem
from search_stub import ucs, astar
from heuristics_stub import zero_heuristic


MAPS = ["small_map.txt", "example_map.txt", "large_map.txt"]
REPEATS = 3


def run_once(algo_name, algo_func, problem):
    start = time.perf_counter()
    path, cost, expanded, max_frontier = algo_func(problem)
    elapsed = time.perf_counter() - start
    return {
        "algo": algo_name,
        "steps": len(path) if path is not None else None,
        "cost": cost,
        "expanded": expanded,
        "max_frontier": max_frontier,
        "time": elapsed,
    }


def average_runs(algo_name, algo_func, map_path):
    results = []
    for _ in range(REPEATS):
        problem = SokobanProblem(map_path)
        results.append(run_once(algo_name, algo_func, problem))

    avg_time = sum(r["time"] for r in results) / REPEATS
    sample = results[0]
    return {
        "algo": algo_name,
        "steps": sample["steps"],
        "cost": sample["cost"],
        "expanded": sample["expanded"],
        "max_frontier": sample["max_frontier"],
        "avg_time": avg_time,
    }


def main():
    print(f"{'Map':<18}{'Algo':<6}{'Steps':<8}{'Cost':<8}{'Expanded':<12}{'MaxFrontier':<14}{'AvgTime(s)':<10}")

    for map_path in MAPS:
        ucs_result = average_runs("UCS", ucs, map_path)
        astar_result = average_runs(
            "A*",
            lambda p: astar(p, zero_heuristic),
            map_path,
        )

        for r in (ucs_result, astar_result):
            print(f"{map_path:<18}{r['algo']:<6}{r['steps']:<8}{r['cost']:<8}"
                  f"{r['expanded']:<12}{r['max_frontier']:<14}{r['avg_time']:<10.4f}")


if __name__ == "__main__":
    main()